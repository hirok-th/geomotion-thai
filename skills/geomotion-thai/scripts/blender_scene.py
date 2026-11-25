"""Blender >=4.2: real DEM geometry, exact polygon mask, animated palette fade.
Run: blender -b -P scripts/blender_scene.py -- project.json [--still 1]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from execution_policy import production_only, enable_cli_production

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: blender -b -P scripts/blender_scene.py -- PROJECT --produce-media [--still N|--build-only]"
        )
        raise SystemExit(0)
    enable_cli_production("--produce-media" in sys.argv)

import bpy, sys, os, json, math, argparse
from pathlib import Path
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from models import make_model, make_arrow, material, cube, cylinder, empty
from common import geography_signature


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def key(o, path, f, v):
    setattr(o, path, v)
    o.keyframe_insert(data_path=path, frame=f)


def smooth(o):
    ad = getattr(o, "animation_data", None)
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = "BEZIER"
                k.handle_left_type = "AUTO_CLAMPED"
                k.handle_right_type = "AUTO_CLAMPED"


def tube(name, points, r, mat):
    d = bpy.data.curves.new(name, "CURVE")
    d.dimensions = "3D"
    d.resolution_u = 1
    d.bevel_depth = r
    d.bevel_resolution = 2
    sp = d.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for pt, co in zip(sp.points, points):
        pt.co = (*co, 1)
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def visibility(o, start, end, fps):
    # Scaling keeps Blender Workbench source self-contained; children inherit.
    scale = tuple(o.scale)
    for t, v in [
        (0, 0),
        (max(0, start - 0.03), 0),
        (start, 1),
        (end, 1),
        (end + 0.03, 0),
    ]:
        key(o, "scale", round(t * fps) + 1, tuple(q * v for q in scale))


@production_only
def build(project, still=None, frames=None, quality=None, build_only=False):
    p = Path(project).resolve()
    base = p.parent
    data = load(base / "data/scene_data.json")
    c = load(p)
    tl = load(base / c["timeline"])
    if geography_signature(c) != geography_signature(data["config"]):
        raise ValueError("Geographic inputs changed; run prepare before rendering")
    for r in c.get("routes", []):
        r["sampled_xyz"] = next(
            q["sampled_xyz"] for q in data["config"]["routes"] if q["id"] == r["id"]
        )
    for r in c.get("places", []):
        r["elevation_m"] = next(
            q.get("elevation_m", 0)
            for q in data["config"]["places"]
            if q["id"] == r["id"]
        )
    fps = c["video"]["fps"]
    dur = tl["duration"]
    g = c["geography"]
    unit = g.get("metres_per_unit", 100000)
    ex = g["vertical_exaggeration"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.frame_end = round(dur * fps)
    s.render.fps = fps
    s.render.resolution_x = c["video"]["width"]
    s.render.resolution_y = c["video"]["height"]
    s.render.resolution_percentage = quality or 100
    s.render.engine = "BLENDER_WORKBENCH"
    s.display.shading.light = "STUDIO"
    s.display.shading.studiolight_rotate_z = 0.3
    s.display.shading.studio_light = "paint.sl"
    s.display.shading.color_type = "MATERIAL"
    s.display.shading.show_shadows = True
    s.display.shading.show_cavity = True
    s.display.shading.cavity_type = "BOTH"
    s.display.shading.curvature_ridge_factor = 0.8
    s.display.shading.curvature_valley_factor = 0.6
    s.display.shading.show_specular_highlight = True
    s.display.shading.show_object_outline = False
    s.display.shading.background_type = "WORLD"
    s.world = bpy.data.worlds.new("GeoMotion world")
    s.world.color = (0.008, 0.023, 0.05)
    s.display.render_aa = "FXAA"
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "Medium High Contrast"
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGB"
    s.render.use_file_extension = True
    origin = g["origin"]
    coslat = math.cos(math.radians(origin[1]))

    def xy(ll):
        return (
            (ll[0] - origin[0]) * 111320 * coslat / unit,
            (ll[1] - origin[1]) * 111320 / unit,
        )

    def world(ll, z=0):
        return (*xy(ll), z)

    ocean = material("Ocean · deep navy", (0.004, 0.042, 0.105, 1))
    cube(
        None,
        "WATER · sea level",
        (0, 0, -0.07),
        (300, 300, 0.1),
        ocean.diffuse_color,
        0,
    )
    # Fine map grid supplies wide-shot spatial context.
    gridmat = material("Map grid", (0.025, 0.15, 0.22, 1))
    for lon in range(math.floor(g["bbox"][0]), math.ceil(g["bbox"][2]) + 1, 2):
        tube(
            "Longitude",
            [world((lon, g["bbox"][1]), -0.012), world((lon, g["bbox"][3]), -0.012)],
            0.005,
            gridmat,
        )
    for lat in range(math.floor(g["bbox"][1]), math.ceil(g["bbox"][3]) + 1, 2):
        tube(
            "Latitude",
            [world((g["bbox"][0], lat), -0.012), world((g["bbox"][2], lat), -0.012)],
            0.005,
            gridmat,
        )
    intros = {x["iso"]: x for x in c.get("countries", [])}
    palette = {}
    coast = material("Border · warm gold", (1, 0.67, 0.12, 1))
    neighbour = material("Neighbour border", (0.1, 0.36, 0.31, 1))

    def terrain_col(h, target):
        t = max(0, min(h / 3000, 1))
        lo = np.array([0.012, 0.16, 0.065])
        hi = np.array([0.25, 0.40, 0.12])
        rgb = lo * (1 - t) + hi * t
        if not target:
            rgb *= 0.72
        return (*rgb, 1)

    def mat_for(iso, terrainbin, flag_rgb):
        k = (iso, terrainbin, flag_rgb)
        if k in palette:
            return palette[k]
        m = material("terrain_" + str(k), terrain_col(terrainbin * 100, iso in intros))
        intro = intros.get(iso)
        if intro:
            e = next(
                e
                for e in tl["events"]
                if e["kind"] == "country_intro" and e["country"] == iso
            )
            t = e["start"]
            v = e["phases"]
            color = tuple(
                (
                    ((q / 255 + 0.055) / 1.055) ** 2.4
                    if q / 255 > 0.04045
                    else q / 255 / 12.92
                )
                for q in flag_rgb
            ) + (1,)
            basecolor = tuple(m.diffuse_color)
            for time, cv in [
                (0, basecolor),
                (t + v["wide"], basecolor),
                (t + v["wide"] + v["flag_in"], color),
                (t + v["zoom_start"], color),
                (t + v["flag_out_end"], basecolor),
            ]:
                key(m, "diffuse_color", round(time * fps) + 1, cv)
            smooth(m)
        palette[k] = m
        return m

    for ob in data["objects"]:
        a = np.load(base / "data" / ob["file"])
        xyz = a["xyz"]
        faces = a["faces"]
        ll = a["lonlat"]
        h = a["heights"]
        iso = ob["iso"]
        intro = intros.get(iso)
        mesh = bpy.data.meshes.new(ob["id"])
        flat = xyz.copy()
        flat[:, 2] = 0.018
        mesh.from_pydata(flat.tolist(), [], faces.tolist())
        mesh.update()
        o = bpy.data.objects.new("LAND · " + ob["id"], mesh)
        bpy.context.collection.objects.link(o)
        o["source"] = "Natural Earth + measured Mapzen DEM"
        o["vertical_exaggeration"] = ex
        o["coordinate_system"] = "local equirectangular"
        o.shape_key_add(name="Flat map")
        relief = o.shape_key_add(name="Measured DEM")
        for v, co in zip(relief.data, xyz):
            v.co = (co[0], co[1], max(0.018, co[2] * ex))
        tilt = next((e for e in tl["events"] if e["kind"] == "country_intro"), None)
        rs = tilt["start"] + tilt["phases"]["zoom_start"] if tilt else 0
        re = tilt["start"] + tilt["phases"]["tilt_end"] if tilt else 3
        key(relief, "value", 1, 0)
        key(relief, "value", int(rs * fps) + 1, 0)
        key(relief, "value", int(re * fps) + 1, 1)
        smooth(o.data.shape_keys)
        image = None
        if intro:
            image = bpy.data.images.load(
                str(base / intro["flag"]["file"]), check_existing=True
            )
            pix = np.array(image.pixels[:], dtype=np.float32).reshape(
                image.size[1], image.size[0], 4
            )
            bb = ob["bbox"]
            # mainland bbox for uniform mapping, multipart share whole country bounds
            same = [q for q in data["objects"] if q["iso"] == iso]
            bb = [
                min(q["bbox"][0] for q in same),
                min(q["bbox"][1] for q in same),
                max(q["bbox"][2] for q in same),
                max(q["bbox"][3] for q in same),
            ]
        slots = {}
        for poly in mesh.polygons:
            ids = np.array(poly.vertices)
            hh = float(np.mean(h[ids]))
            hb = max(0, min(30, round(hh / 100)))
            flag = (0, 0, 0)
            if intro:
                center = np.mean(ll[ids], axis=0)
                u = (center[0] - bb[0]) / (bb[2] - bb[0])
                v = (center[1] - bb[1]) / (bb[3] - bb[1])
                ix = min(image.size[0] - 1, max(0, int(u * image.size[0])))
                iy = min(image.size[1] - 1, max(0, int(v * image.size[1])))
                flag = tuple(
                    int(round(float(q) * 255 / 8) * 8) for q in pix[iy, ix, :3]
                )
                flag = tuple(min(255, q) for q in flag)
            m = mat_for(iso, hb, flag)
            if m.name not in slots:
                slots[m.name] = len(mesh.materials)
                mesh.materials.append(m)
            poly.material_index = slots[m.name]
            poly.use_smooth = True
        # Exact source polygon perimeter; relief is sampled via nearest land vertex.
        for ri, ring in enumerate(ob["rings"]):
            pts = []
            for lon, lat in ring:
                d2 = (ll[:, 0] - lon) ** 2 + (ll[:, 1] - lat) ** 2
                zz = max(0.018, float(xyz[int(np.argmin(d2)), 2]) * ex)
                pts.append((*xy((lon, lat)), zz + 0.026))
            line = tube(
                "BORDER · " + ob["id"] + f" · {ri}",
                pts,
                0.014 if intro else 0.004,
                coast if intro else neighbour,
            )
            # Curve shape keys move the centreline without collapsing the bevel normals.
            flat_border = line.shape_key_add(name="Flat border")
            relief_border = line.shape_key_add(name="Measured border")
            for point in flat_border.data:
                point.co.z = 0.043
            key(relief_border, "value", 1, 0)
            key(relief_border, "value", round(rs * fps) + 1, 0)
            key(relief_border, "value", round(re * fps) + 1, 1)
            smooth(line.data.shape_keys)
    print("Built land and borders", flush=True)
    # Rivers follow measured elevations and stay separate from ground.
    rivermat = material("Rivers", (0.035, 0.47, 0.61, 1))
    for i, r in enumerate(load(base / "data/rivers.json")):
        pts = [(a, b, max(0.018, z * ex) + 0.009) for a, b, z in r["xyz"]]
        o = tube("RIVER · " + str(r.get("name") or i), pts, 0.006, rivermat)
        visibility(o, re + 0.1, dur, fps)
    # Landmark symbols and pins. Native model z is offset to sit on land.
    for place in c.get("places", []):
        pos = world(
            place["lonlat"], max(0.018, place.get("elevation_m", 0) / unit * ex) + 0.03
        )
        start = place.get("show_at", re)
        root = make_model(place.get("icon", "pin"), "PLACE · " + place["id"])
        root.location = pos
        root.scale = (place.get("scale", 0.28),) * 3
        visibility(root, start, dur, fps)
    # Routes use a single sampled curve for both line drawing and vehicle positions.
    for route in c.get("routes", []):
        evt = next(
            e
            for e in tl["events"]
            if e["kind"] == "route" and e["route"] == route["id"]
        )
        a, b = evt["start"], evt["end"]
        pts = np.array(route["sampled_xyz"], float)
        pts[:, 2] = np.maximum(0.018, pts[:, 2] * ex) + 0.07
        color = material(
            "Route " + route["id"], tuple(route.get("color", [1, 0.45, 0.015, 1]))
        )
        width = route.get("width", 0.035)
        style = route.get("style", "solid")
        if style == "dashed":
            for i in range(0, len(pts) - 3, 9):
                o = tube("ROUTE · dashed", pts[i : i + 5], width, color)
                visibility(o, a + (b - a) * i / (len(pts) - 1), dur, fps)
        else:
            o = tube("ROUTE · " + route["id"], pts, width, color)
            key(o.data, "bevel_factor_end", 1, 0)
            key(o.data, "bevel_factor_end", round(a * fps) + 1, 0)
            key(o.data, "bevel_factor_end", round(b * fps) + 1, 1)
            smooth(o.data)
        vehicle = make_model(route.get("vehicle", "train"), "VEHICLE · " + route["id"])
        vehicle.scale = (route.get("vehicle_scale", 0.25),) * 3
        visibility(vehicle, a, dur, fps)
        arrow = make_arrow(
            "ARROW · " + route["id"], route.get("arrowhead", "triangle"), color
        )
        visibility(arrow, a, dur, fps)
        # Equal arc-length parameterization prevents acceleration at dense control points.
        dist = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
        for frame in range(round(a * fps) + 1, round(b * fps) + 2):
            u = min(1, (frame - 1 - a * fps) / ((b - a) * fps))
            dd = u * dist[-1]
            idx = min(len(pts) - 2, max(0, np.searchsorted(dist, dd) - 1))
            q = (dd - dist[idx]) / max(1e-12, dist[idx + 1] - dist[idx])
            pos = pts[idx] * (1 - q) + pts[idx + 1] * q
            delta = pts[idx + 1] - pts[idx]
            vehicle.location = pos + np.array([0, 0, route.get("altitude_units", 0)])
            vehicle.rotation_euler.z = -math.atan2(delta[0], delta[1])
            vehicle.keyframe_insert("location", frame=frame)
            vehicle.keyframe_insert("rotation_euler", frame=frame)
            arrow.location = pos + np.array([0, 0, 0.05])
            arrow.rotation_euler.z = vehicle.rotation_euler.z
            arrow.keyframe_insert("location", frame=frame)
            arrow.keyframe_insert("rotation_euler", frame=frame)
        for obj in [vehicle, arrow]:
            for fc in obj.animation_data.action.fcurves:
                if fc.data_path in ["location", "rotation_euler"]:
                    for k in fc.keyframe_points:
                        k.interpolation = "LINEAR"
        if route.get("mode") == "rail":
            # Schematic sleepers are subordinate to the bright moving route.
            railmat = material("Rail silver", (0.25, 0.34, 0.36, 1))
            for off in [-0.045, 0.045]:
                rail = pts.copy()
                dv = np.gradient(pts[:, :2], axis=0)
                norm = np.c_[-dv[:, 1], dv[:, 0]]
                norm /= np.maximum(1e-9, np.linalg.norm(norm, axis=1))[:, None]
                rail[:, :2] += norm * off
                rail[:, 2] -= 0.035
                rr = tube("Rail", rail, 0.009, railmat)
                visibility(rr, a, dur, fps)
            for i in range(0, len(pts), 5):
                sleeper = cube(
                    None,
                    "Sleeper",
                    pts[i] + np.array([0, 0, -0.045]),
                    (0.14, 0.024, 0.018),
                    "black",
                    0,
                )
                delta = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
                sleeper.rotation_euler.z = -math.atan2(delta[0], delta[1])
                visibility(sleeper, a, dur, fps)
    # Camera frames carry map coordinates; portrait and landscape framing are independent.
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "CAMERA · GeoMotion"
    s.camera = cam
    cam.data.lens = 45
    cam.data.sensor_width = 36
    cam.data.sensor_fit = "HORIZONTAL"
    aspect = c["video"]["width"] / c["video"]["height"]
    preset = "landscape" if aspect > 1 else "portrait"
    for k in c["camera"][preset]:
        target = np.array(world(k["target"], k.get("target_z", 0.08)))
        tilt = math.radians(k.get("tilt", 0))
        az = math.radians(k.get("azimuth", 0))
        distance = k["width"] / (2 * math.tan(cam.data.angle_x / 2))
        offset = (
            np.array(
                [
                    math.sin(az) * math.sin(tilt),
                    -math.cos(az) * math.sin(tilt),
                    math.cos(tilt),
                ]
            )
            * distance
        )
        cam.location = target + offset
        cam.rotation_euler = (
            (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        )
        cam.keyframe_insert("location", frame=round(k["time"] * fps) + 1)
        cam.keyframe_insert("rotation_euler", frame=round(k["time"] * fps) + 1)
    smooth(cam)
    print("Built camera, routes and objects", flush=True)
    # A sidecar stores camera-projected overlay anchors so Thai text uses HarfBuzz/libass.
    from bpy_extras.object_utils import world_to_camera_view

    anchors = {}
    for frame in range(1, s.frame_end + 1):
        s.frame_set(frame)
        arr = {}
        for place in c.get("places", []):
            pp = Vector(
                world(
                    place["lonlat"],
                    max(0.018, place.get("elevation_m", 0) / unit * ex) + 0.22,
                )
            )
            q = world_to_camera_view(s, cam, pp)
            arr[place["id"]] = [
                q.x * s.render.resolution_x,
                (1 - q.y) * s.render.resolution_y,
                float(q.z),
            ]
        anchors[str(frame)] = arr
    (base / "build").mkdir(exist_ok=True)
    (base / "build/anchors.json").write_text(json.dumps(anchors))
    s.frame_set(1)
    s.render.filepath = str(base / "build/frames/frame_")
    Path(s.render.filepath).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(base / "build/GeoMotionThai.blend"))
    if build_only:
        return
    if still:
        s.frame_set(still)
        s.render.filepath = str(base / f"build/still_{still:04d}.png")
        bpy.ops.render.render(write_still=True)
    elif frames:
        a, b = map(int, frames.split(":"))
        s.frame_start = a
        s.frame_end = b
        bpy.ops.render.render(animation=True)
    else:
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project")
    ap.add_argument("--still", type=int)
    ap.add_argument("--frames")
    ap.add_argument("--quality", type=int)
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--produce-media", action="store_true")
    a = ap.parse_args(args)
    build(a.project, a.still, a.frames, a.quality, a.build_only)
