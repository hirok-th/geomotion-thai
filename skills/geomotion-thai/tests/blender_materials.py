"""Regression: dynamic bpy colour arrays must not alias different symbol materials."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from execution_policy import enable_cli_production

enable_cli_production("--produce-media" in sys.argv)
import bpy, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from models import cube, material, make_arrow

bpy.ops.wm.read_factory_settings(use_empty=True)
ocean = material("Ocean", (0.004, 0.042, 0.105, 1))
water = cube(None, "Water", (0, 0, 0), (4, 4, 0.1), ocean.diffuse_color, 0)
before = tuple(water.data.materials[0].diffuse_color)
for i, style in enumerate(["triangle", "chevron", "diamond", "double"]):
    color = material("Route" + str(i), (1, 0.5 + i * 0.1, 0.025, 1))
    arrow = make_arrow("Arrow" + str(i), style, color)
    assert (
        tuple(water.data.materials[0].diffuse_color) == before
    ), "Arrow material modified water"
    for ch in arrow.children:
        assert (
            ch.data.materials[0] != water.data.materials[0]
        ), "Arrow and water share mutable material"
print("PASS: four arrow styles preserve independent water material", flush=True)
