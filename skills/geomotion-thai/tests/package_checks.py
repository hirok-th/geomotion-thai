"""Offline validation. Never launches a renderer or calls a media service."""

import ast, contextlib, importlib.util, io, json, re, runpy, socket, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from execution_policy import (
    MediaProductionDisabled,
    production_only,
    production_request,
)


class PackageChecks(unittest.TestCase):
    def test_upload_archives_and_reject_loose_root_files(self):
        import build_package, zipfile

        with tempfile.TemporaryDirectory() as d:
            for kind in ["skill", "claude-plugin"]:
                path = Path(d) / f"{kind}.zip"
                with patch(
                    "socket.socket.connect",
                    side_effect=AssertionError("Network forbidden"),
                ), patch(
                    "subprocess.Popen",
                    side_effect=AssertionError("External process forbidden"),
                ):
                    self.assertTrue(build_package.build(path, kind)["valid"])
                with zipfile.ZipFile(path) as z:
                    if kind == "claude-plugin":
                        self.assertIn(
                            "geomotion-thai/.claude-plugin/plugin.json", z.namelist()
                        )
                        self.assertIn(
                            "geomotion-thai/skills/geomotion-thai/SKILL.md",
                            z.namelist(),
                        )
                    else:
                        self.assertIn("geomotion-thai/SKILL.md", z.namelist())
                    self.assertNotIn("MANIFEST.sha256", z.namelist())
                with zipfile.ZipFile(path, "a") as z:
                    z.writestr(
                        "MANIFEST.sha256", "loose root file reproduces failed upload"
                    )
                with self.assertRaisesRegex(ValueError, "top-level folder"):
                    build_package.validate_archive(path, kind)

    def test_python_syntax_without_execution(self):
        for p in [
            *ROOT.joinpath("scripts").glob("*.py"),
            *ROOT.joinpath("tests").glob("*.py"),
        ]:
            compile(p.read_text(encoding="utf-8"), str(p), "exec")

    def test_json_and_skill_frontmatter(self):
        for p in ROOT.rglob("*.json"):
            json.loads(p.read_text(encoding="utf-8"))
        import yaml

        raw = (ROOT / "SKILL.md").read_text()
        front = yaml.safe_load(raw.split("---", 2)[1])
        self.assertEqual(front["name"], "geomotion-thai")
        self.assertTrue(front["description"])
        self.assertIn("package-only", raw)
        self.assertIn("--produce-media", raw)
        metadata = yaml.safe_load((ROOT / "agents/openai.yaml").read_text())
        self.assertIn("interface", metadata)

    def test_referenced_docs_and_resources_exist(self):
        for p in [ROOT / "SKILL.md", *ROOT.joinpath("references").glob("*.md")]:
            for target in re.findall(r"\]\(([^)]+)\)", p.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                dest = (p.parent / target.split("#")[0]).resolve()
                self.assertTrue(dest.is_file(), f"Broken reference: {p.name}: {target}")
        for rel in [
            "assets/icons/GeoMotion_Objects.blend",
            "assets/fonts/Kanit-Medium.ttf",
            "assets/fonts/Kanit-SemiBold.ttf",
            "assets/flags/th.png",
        ]:
            self.assertTrue((ROOT / rel).is_file())

    def test_service_defaults_and_secret_separation(self):
        c = json.loads((ROOT / "config/services.example.json").read_text())
        self.assertEqual(c["activation"]["default_mode"], "package_only")
        self.assertFalse(c["activation"]["connect_during_install"])
        self.assertFalse(c["gemini_api"]["enabled"])
        self.assertEqual(c["gemini_api"]["api_key_env"], "GEMINI_API_KEY")
        self.assertTrue(c["gemini_api"]["requires_explicit_user_authorization"])
        forbidden = {
            "api_key",
            "password",
            "cookie",
            "access_token",
            "refresh_token",
            "private_key",
        }

        def check(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    self.assertFalse(k.lower() in forbidden and v not in [None, ""])
                    check(v)
            elif isinstance(x, list):
                for v in x:
                    check(v)

        check(c)

    def test_production_context_is_opt_in_and_resets(self):
        calls = []

        @production_only
        def harmless():
            calls.append("called")

        with self.assertRaises(MediaProductionDisabled):
            harmless()
        with production_request(True):
            harmless()
        with self.assertRaises(MediaProductionDisabled):
            harmless()
        self.assertEqual(calls, ["called"])

    def test_default_cli_blocks_before_external_work(self):
        cases = [
            ("scripts/geomotion.py", ["prepare", "missing.json"]),
            ("scripts/geomotion.py", ["render", "missing.json", "--visual-preview"]),
            ("scripts/geomotion.py", ["compose", "missing.json", "--visual-preview"]),
            ("scripts/geomotion.py", ["qc", "missing.json", "--visual-preview"]),
            ("scripts/prepare_geo.py", ["missing.json"]),
            ("scripts/render_frames.py", ["missing.json"]),
            ("scripts/compose.py", ["missing.json", "--visual-preview"]),
            ("scripts/qc.py", ["missing.json", "--visual-preview"]),
            ("scripts/google_tts.py", ["models"]),
            ("scripts/google_tts.py", ["voices"]),
            (
                "scripts/google_tts.py",
                ["speak", "--project", "missing.json", "--allow-api"],
            ),
            ("scripts/audio_timeline.py", ["candidate", "missing.json"]),
            ("scripts/audio_timeline.py", ["retime", "missing.json"]),
            ("scripts/export_assets.py", []),
            ("scripts/blender_scene.py", ["--", "missing.json"]),
            ("tests/blender_materials.py", []),
        ]
        for rel, args in cases:
            out = io.StringIO()
            err = io.StringIO()
            blocked = False
            with patch.object(sys, "argv", [str(ROOT / rel), *args]), patch(
                "socket.socket.connect", side_effect=AssertionError("Network forbidden")
            ), patch(
                "subprocess.Popen",
                side_effect=AssertionError("External process forbidden"),
            ), contextlib.redirect_stdout(
                out
            ), contextlib.redirect_stderr(
                err
            ):
                try:
                    runpy.run_path(str(ROOT / rel), run_name="__main__")
                except MediaProductionDisabled:
                    blocked = True
                except SystemExit as e:
                    blocked = (
                        e.code == 2 and "Media production is disabled" in err.getvalue()
                    )
            self.assertTrue(
                blocked, f"Default command did not stop safely: {rel} {args}"
            )

    def test_programmatic_media_functions_block(self):
        import prepare_geo, render_frames, compose, audio_timeline, google_tts, qc

        functions = [
            lambda: prepare_geo.prepare("missing.json"),
            lambda: render_frames.render("missing.json"),
            lambda: compose.compose("missing.json"),
            lambda: compose.effects(Path("missing.json")),
            lambda: audio_timeline.candidate("missing.json", "small"),
            lambda: google_tts.call("models"),
            lambda: google_tts.catalog("models", "models"),
            lambda: google_tts.speak("missing.json", True),
            lambda: qc.qc("missing.json"),
        ]
        with patch(
            "socket.socket.connect", side_effect=AssertionError("Network forbidden")
        ), patch(
            "subprocess.Popen", side_effect=AssertionError("External process forbidden")
        ):
            for f in functions:
                with self.assertRaises(MediaProductionDisabled):
                    f()

    def test_api_connection_stays_disabled(self):
        import google_tts

        with patch.object(
            google_tts, "urlopen", side_effect=AssertionError("API forbidden")
        ):
            with self.assertRaisesRegex(RuntimeError, "API is disabled"):
                google_tts.load_api_settings()

    def test_installation_paths_are_read_only_plans(self):
        for platform, folder in [
            ("claude", ".claude/skills"),
            ("codex", ".agents/skills"),
            ("antigravity", ".agents/skills"),
        ]:
            with tempfile.TemporaryDirectory() as d:
                out = io.StringIO()
                with patch.object(
                    sys,
                    "argv",
                    ["install_skill.py", "--platform", platform, "--workspace", d],
                ), contextlib.redirect_stdout(out):
                    runpy.run_path(
                        str(ROOT / "scripts/install_skill.py"), run_name="__main__"
                    )
                v = json.loads(out.getvalue())
                self.assertFalse(v["applied"])
                self.assertIn(folder, v["destination"])
                self.assertFalse(Path(v["destination"]).exists())

    def test_project_templates_are_text_only_in_both_aspects(self):
        import geomotion

        with tempfile.TemporaryDirectory() as d:
            for land, size in [(False, [1080, 1920]), (True, [1920, 1080])]:
                dest = Path(d) / str(land)
                with contextlib.redirect_stdout(io.StringIO()):
                    geomotion.new(dest, "[future topic]", land)
                c = json.loads((dest / "project.json").read_text())
                self.assertEqual([c["video"]["width"], c["video"]["height"]], size)
                settings = json.loads((dest / "services.json").read_text())
                self.assertFalse(settings["gemini_api"]["enabled"])
                self.assertTrue(
                    all(
                        p.suffix in [".json", ".txt"]
                        for p in dest.rglob("*")
                        if p.is_file()
                    )
                )

    def test_doctor_does_not_launch_binaries(self):
        import geomotion

        with patch(
            "subprocess.run", side_effect=AssertionError("Binary probe forbidden")
        ), patch(
            "subprocess.check_output",
            side_effect=AssertionError("Binary probe forbidden"),
        ), contextlib.redirect_stdout(
            io.StringIO()
        ):
            r = geomotion.doctor()
        self.assertFalse(r["binaries_probed"])
        self.assertEqual(r["default_mode"], "package_only")


if __name__ == "__main__":
    unittest.main(verbosity=2)
