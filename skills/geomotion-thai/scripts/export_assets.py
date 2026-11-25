"""Regenerate existing icon resources only after a user clip request."""

import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from execution_policy import production_only, enable_cli_production


@production_only
def export_assets():
    import bpy, sys, math, json
    from pathlib import Path
    from mathutils import Vector

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from models import make_model

    root = Path(__file__).resolve().parents[1]
    out = root / "assets/icons"
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.world = bpy.data.worlds.new("World")
    s.world.color = (0.02, 0.04, 0.07)
    s.render.engine = "BLENDER_WORKBENCH"
    s.display.shading.light = "STUDIO"
    s.display.shading.studio_light = "paint.sl"
    s.display.shading.color_type = "MATERIAL"
    s.display.shading.show_shadows = True
    s.display.shading.show_cavity = True
    s.display.shading.cavity_type = "BOTH"
    s.display.shading.show_specular_highlight = True
    s.display.render_aa = "16"
    s.render.film_transparent = True
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.render.resolution_x = 400
    s.render.resolution_y = 400
    s.render.resolution_percentage = 100
    s.view_settings.view_transform = "Standard"
    bpy.ops.object.camera_add(location=(3.2, 4.6, 3.4))
    cam = bpy.context.object
    cam.rotation_euler = (
        (Vector((0, -0.2, 0.2)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    )
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.1
    s.camera = cam
    kinds = [
        "plane",
        "train",
        "track",
        "ship",
        "car",
        "building",
        "city",
        "factory",
        "mountain",
        "tree",
        "dam",
        "reservoir",
        "pin",
    ]
    roots = {}
    for kind in kinds:
        r = make_model(kind)
        roots[kind] = r

        def descendants(o):
            yield o
            for ch in o.children:
                yield from descendants(ch)

        for o in descendants(r):
            o.hide_render = True
    for kind, r in roots.items():
        for o in descendants(r):
            o.hide_render = False
        s.render.filepath = str(out / f"{kind}.png")
        bpy.ops.render.render(write_still=True)
        for o in descendants(r):
            o.hide_render = True
    for i, (kind, r) in enumerate(roots.items()):
        r.location = ((i % 4) * 3, (i // 4) * 3, 0)
        for o in descendants(r):
            o.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "GeoMotion_Objects.blend"))
    (out / "catalog.json").write_text(
        json.dumps(
            {
                "license": "Original procedural models; same license as package code",
                "models": kinds,
                "forward_axis": "+Y",
                "up_axis": "+Z",
                "units": "symbolic",
                "editable_layers": True,
                "reference_match": "stylized silhouette approximation, not photoreal reconstruction; see references/asset-comparison.md",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--produce-media", action="store_true")
    a = ap.parse_args(args)
    enable_cli_production(a.produce_media)
    export_assets()
