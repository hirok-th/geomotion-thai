"""Functional regression tests for data integrity and final-export guards.
No credentials, network synthesis or production publication is needed.
"""

import unittest, sys, json, tempfile, shutil, os, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import ROOT, read, write, geography_signature
from validate_project import validate
from compose import wrap, srt_time
from PIL import Image, ImageFont


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "project"
        shutil.copytree(ROOT / "templates/project", self.base)
        self.p = self.base / "project.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_final_requires_real_reviewed_audio(self):
        self.assertTrue(validate(self.p, True)["valid"])
        r = validate(self.p, False)
        self.assertFalse(r["valid"])
        self.assertIn("Narration absent; final export blocked", r["errors"])

    def test_watermark_requires_both_instruction_and_logo(self):
        c = read(self.p)
        logo = self.base / "logo.png"
        Image.new("RGBA", (60, 30), (255, 0, 0, 120)).save(logo)
        c["watermark"].update(enabled=True, user_requested=False, file="logo.png")
        write(self.p, c)
        self.assertFalse(validate(self.p, True)["valid"])
        c["watermark"]["user_requested"] = True
        write(self.p, c)
        self.assertTrue(validate(self.p, True)["valid"])
        logo.unlink()
        self.assertFalse(validate(self.p, True)["valid"])

    def test_new_audio_and_geo_inputs_invalidate_state(self):
        c = read(self.p)
        sig = geography_signature(c)
        c["routes"][0]["sampled_xyz"] = [[0, 0, 0]]
        self.assertEqual(sig, geography_signature(c))
        c["routes"][0]["coordinates"][0][0] += 0.1
        self.assertNotEqual(sig, geography_signature(c))
        (self.base / "data").mkdir()
        write(
            self.base / "data/scene_data.json",
            {"config": read(self.p), "objects": [{"iso": "THA"}]},
        )
        write(self.p, c)
        self.assertIn(
            "Geographic configuration changed; run prepare again",
            validate(self.p, True)["errors"],
        )

    def test_thai_shaping_wrap_and_srt_rounding(self):
        font = ImageFont.truetype(
            str(ROOT / "assets/fonts/Kanit-SemiBold.ttf"),
            58,
            layout_engine=ImageFont.Layout.RAQM,
        )
        lines = wrap("ประเทศไทย\nมีอะไรมากกว่าที่เห็นบนแผนที่", font, 770)
        self.assertLessEqual(len(lines), 2)
        self.assertTrue(all(font.getlength(x) <= 770 for x in lines))
        self.assertEqual(srt_time(59.9996), "00:01:00,000")

    def test_all_icons_are_actual_transparent_renders(self):
        kinds = read(ROOT / "assets/icons/catalog.json")["models"]
        self.assertEqual(len(kinds), 13)
        for kind in kinds:
            im = Image.open(ROOT / "assets/icons" / f"{kind}.png")
            self.assertEqual(im.mode, "RGBA")
            alpha = im.getchannel("A")
            self.assertEqual(alpha.getextrema()[0], 0)
            self.assertGreaterEqual(alpha.getextrema()[1], 250)

    def test_local_platform_adapters_are_concrete_dry_runs(self):
        for platform, folder in [
            ("claude", ".claude/skills"),
            ("codex", ".agents/skills"),
            ("antigravity", ".agents/skills"),
        ]:
            out = subprocess.check_output(
                [
                    sys.executable,
                    str(ROOT / "scripts/install_skill.py"),
                    "--platform",
                    platform,
                    "--workspace",
                    str(self.base),
                ],
                text=True,
            )
            v = json.loads(out)
            self.assertIn(folder, v["destination"])
            self.assertFalse(v["applied"])
            self.assertFalse(Path(v["destination"]).exists())


class PreparedGeometry(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("GEOMOTION_TEST_PROJECT"),
        "Set GEOMOTION_TEST_PROJECT for cached measured data checks",
    )
    def test_country_mesh_preserves_polygon_area_and_measured_relief(self):
        import numpy as np
        from shapely.geometry import shape, box

        p = Path(os.environ["GEOMOTION_TEST_PROJECT"])
        c = read(p)
        b = p.parent
        d = read(b / "data/scene_data.json")
        total = 0
        heights = []
        for o in d["objects"]:
            if o["iso"] != "THA":
                continue
            a = np.load(b / "data" / o["file"])
            ll = a["lonlat"]
            f = a["faces"]
            tri = ll[f]
            cross = (tri[:, 1, 0] - tri[:, 0, 0]) * (tri[:, 2, 1] - tri[:, 0, 1]) - (
                tri[:, 2, 0] - tri[:, 0, 0]
            ) * (tri[:, 1, 1] - tri[:, 0, 1])
            total += np.abs(cross).sum() / 2
            heights += a["heights"].tolist()
        source = read(ROOT / "assets/geodata/countries.geojson")
        th = next(
            shape(x["geometry"])
            for x in source["features"]
            if x["properties"]["ADM0_A3"] == "THA"
        ).intersection(box(*c["geography"]["bbox"]))
        self.assertAlmostEqual(total, th.area, places=7)
        self.assertGreater(max(heights) - min(heights), 2000)
        self.assertEqual(d["terrain_type"], "measured_dem_mesh")


if __name__ == "__main__":
    unittest.main(verbosity=2)
