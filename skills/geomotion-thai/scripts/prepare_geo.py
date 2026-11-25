"""Prepare verified boundaries and Terrarium DEM as reusable mesh data.
Coordinates: WGS84 lon,lat; local equirectangular metres centred at project origin.
Never synthesizes elevation. Downloads are bounded, cached, and hashed.
"""

import argparse, io, json, math, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from shapely.geometry import shape, box, Polygon, LineString, mapping
import triangle
from execution_policy import production_only, enable_cli_production

from common import ROOT, read, write, digest


def download(url, p):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        with urlopen(
            Request(url, headers={"User-Agent": "GeoMotionThai/1.0"}), timeout=60
        ) as r:
            data = r.read()
        tmp = p.with_suffix(p.suffix + ".part")
        tmp.write_bytes(data)
        tmp.replace(p)
    return p


def tile_xy(lon, lat, z):
    return (lon + 180) / 360 * 2**z, (
        1 - math.asinh(math.tan(math.radians(lat))) / math.pi
    ) / 2 * 2**z


def make_dem(bbox, z, cache):
    west, south, east, north = bbox
    ax, ay = tile_xy(west, north, z)
    bx, by = tile_xy(east, south, z)
    x0, y0, x1, y1 = math.floor(ax), math.floor(ay), math.floor(bx), math.floor(by)
    jobs = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
    if len(jobs) > 256:
        raise ValueError("DEM request exceeds 256 tiles; lower zoom or crop region")

    def job(xy):
        x, y = xy
        url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
        p = download(url, cache / f"{z}-{x}-{y}.png")
        a = np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)
        return (
            x,
            y,
            a[:, :, 0] * 256 + a[:, :, 1] + a[:, :, 2] / 256 - 32768,
            {"url": url, "sha256": digest(p)},
        )

    results = list(ThreadPoolExecutor(6).map(job, jobs))
    mosaic = np.zeros(((y1 - y0 + 1) * 256, (x1 - x0 + 1) * 256), np.float32)
    for x, y, a, _ in results:
        mosaic[
            (y - y0) * 256 : (y - y0 + 1) * 256, (x - x0) * 256 : (x - x0 + 1) * 256
        ] = a

    def sample(vertices):
        a = np.asarray(vertices)
        lat = np.radians(a[:, 1])
        tx = (a[:, 0] + 180) / 360 * 2**z
        ty = (1 - np.arcsinh(np.tan(lat)) / np.pi) / 2 * 2**z
        return map_coordinates(
            mosaic,
            [(ty - y0) * 256 - 0.5, (tx - x0) * 256 - 0.5],
            order=1,
            mode="nearest",
        )

    return sample, [q[3] for q in results]


def polygons(g):
    if g.geom_type == "Polygon":
        yield g
    elif hasattr(g, "geoms"):
        for p in g.geoms:
            yield from polygons(p)


def triangulate(poly, area):
    vs = []
    segments = []
    holes = []
    for ri, ring in enumerate([poly.exterior, *poly.interiors]):
        coords = list(ring.coords)[:-1]
        start = len(vs)
        vs += coords
        segments += [
            (start + i, start + (i + 1) % len(coords)) for i in range(len(coords))
        ]
        if ri:
            holes.append(list(Polygon(ring).representative_point().coords)[0])
    data = {"vertices": np.array(vs), "segments": np.array(segments)}
    if holes:
        data["holes"] = np.array(holes)
    t = triangle.triangulate(data, f"pq20a{area}")
    return t["vertices"], t["triangles"]


@production_only
def prepare(project):
    p = Path(project).resolve()
    base = p.parent
    c = read(p)
    g = c["geography"]
    bbox = g["bbox"]
    clip = box(*bbox)
    if not (-180 <= bbox[0] < bbox[2] <= 180 and -85 <= bbox[1] < bbox[3] <= 85):
        raise ValueError("Use non-wrapping bbox within ±85° latitude")
    source = ROOT / "assets/geodata/countries.geojson"
    fc = read(source)
    sample, tiles = make_dem(bbox, g.get("dem_zoom", 7), base / "data/cache")
    origin = g["origin"]
    coslat = math.cos(math.radians(origin[1]))
    unit = g.get("metres_per_unit", 100000)
    objects = []
    dest = base / "data"
    dest.mkdir(parents=True, exist_ok=True)
    for f in fc["features"]:
        geom = shape(f["geometry"])
        if not geom.intersects(clip):
            continue
        prop = f["properties"]
        iso = prop.get("ADM0_A3") or prop.get("ISO_A3")
        parts = list(polygons(geom.intersection(clip)))
        for pi, poly in enumerate(parts):
            if poly.area < 0.002:
                continue
            vs, faces = triangulate(
                poly,
                (
                    g.get("triangle_area_deg2", 0.008)
                    if iso in {q["iso"] for q in c.get("countries", [])}
                    else g.get("neighbour_triangle_area_deg2", 0.012)
                ),
            )
            heights = sample(vs)
            xyz = np.c_[
                (vs[:, 0] - origin[0]) * 111320 * coslat / unit,
                (vs[:, 1] - origin[1]) * 111320 / unit,
                np.maximum(heights, 2) / unit,
            ]
            name = f"{iso}_{pi}"
            np.savez_compressed(
                dest / f"{name}.npz",
                xyz=xyz,
                faces=faces.astype(np.int32),
                lonlat=vs,
                heights=heights,
            )
            objects.append(
                {
                    "id": name,
                    "iso": iso,
                    "name": prop.get("NAME_EN", prop.get("ADMIN")),
                    "file": f"{name}.npz",
                    "bbox": list(poly.bounds),
                    "rings": [
                        list(poly.exterior.coords),
                        *[list(r.coords) for r in poly.interiors],
                    ],
                    "vertices": len(vs),
                    "faces": len(faces),
                }
            )
    # Resample elevations for explicit landmarks and all route samples, so runtime has no network.
    for place in c.get("places", []):
        q = np.asarray([place["lonlat"]])
        place["elevation_m"] = float(max(0, sample(q)[0]))
    # Optional real river line data, clipped to project extent.
    rivers = []
    if g.get("rivers", True):
        url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_rivers_lake_centerlines.geojson"
        rp = download(url, ROOT / "assets/geodata/rivers.geojson")
        for f in read(rp)["features"]:
            line = shape(f["geometry"]).intersection(clip)
            for ln in (
                [line] if line.geom_type == "LineString" else getattr(line, "geoms", [])
            ):
                if ln.geom_type != "LineString" or ln.length < 0.2:
                    continue
                a = np.asarray(ln.coords)
                h = sample(a)
                rivers.append(
                    {
                        "name": f["properties"].get("name"),
                        "xyz": np.c_[
                            (a[:, 0] - origin[0]) * 111320 * coslat / unit,
                            (a[:, 1] - origin[1]) * 111320 / unit,
                            np.maximum(h, 2) / unit,
                        ].tolist(),
                    }
                )
    write(dest / "rivers.json", rivers)
    # routes use densified Catmull-Rom curves. Ground/sea positions sample actual terrain.
    from scipy.interpolate import CubicSpline

    for route in c.get("routes", []):
        points = np.asarray(route["coordinates"], float)
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
        if len(d) < 2 or d[-1] == 0:
            raise ValueError("Route requires distinct coordinates")
        ll = CubicSpline(d, points, axis=0, bc_type="natural")(
            np.linspace(0, d[-1], 241)
        )
        arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ll, axis=0), axis=1))]
        ll = np.c_[
            np.interp(np.linspace(0, arc[-1], 241), arc, ll[:, 0]),
            np.interp(np.linspace(0, arc[-1], 241), arc, ll[:, 1]),
        ]
        h = np.maximum(sample(ll), 0)
        if route.get("mode") == "sea":
            h[:] = 0
        route["sampled_xyz"] = np.c_[
            (ll[:, 0] - origin[0]) * 111320 * coslat / unit,
            (ll[:, 1] - origin[1]) * 111320 / unit,
            h / unit,
        ].tolist()
        route["schematic"] = route.get("schematic", True)
    # Download referenced modern flag PNGs, never guess historical flag.
    for intro in c.get("countries", []):
        flag = intro.get("flag", {})
        if not flag.get("source_url") or not flag.get("valid_from"):
            raise ValueError("Country flag needs source_url and valid_from")
        target = base / flag["file"]
        bundled = ROOT / "assets/flags/th.png"
        if (
            flag["source_url"] == "https://flagcdn.com/w640/th.png"
            and not target.exists()
            and bundled.exists()
        ):
            import shutil

            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bundled, target)
        else:
            download(flag["source_url"], target)
    write(
        dest / "scene_data.json",
        {
            "objects": objects,
            "config": c,
            "dem_tiles": tiles,
            "boundary_sha256": digest(source),
            "terrain_type": "measured_dem_mesh",
            "vertical_exaggeration": g["vertical_exaggeration"],
            "projection": "local equirectangular; WGS84, metre scale, north up",
            "limitations": [
                "Natural Earth 1:50m generalized boundaries; not cadastral",
                "Coarse regional DEM; choose a finer dataset for city/flood analysis",
                "No antimeridian or polar support in this renderer",
            ],
        },
    )
    write(
        dest / "geodata_manifest.json",
        {
            "boundary": {
                "source": "Natural Earth 1:50m",
                "url": "https://www.naturalearthdata.com/",
                "sha256": digest(source),
                "license": "public domain",
            },
            "dem": {
                "provider": "Mapzen Terrain Tiles on AWS",
                "attribution": "https://github.com/tilezen/joerd/blob/master/docs/attribution.md",
                "accessed": datetime.date.today().isoformat(),
                "tiles": tiles,
            },
            "vertical_exaggeration": g["vertical_exaggeration"],
            "routes": [
                {"id": r["id"], "schematic": r["schematic"], "source": r.get("source")}
                for r in c.get("routes", [])
            ],
        },
    )
    print(
        json.dumps(
            {
                "objects": len(objects),
                "vertices": sum(o["vertices"] for o in objects),
                "dem_tiles": len(tiles),
                "output": str(dest),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project")
    ap.add_argument(
        "--produce-media",
        action="store_true",
        help="Only after an explicit user clip request",
    )
    a = ap.parse_args()
    enable_cli_production(a.produce_media)
    prepare(a.project)
