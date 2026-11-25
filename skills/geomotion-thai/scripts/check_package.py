"""Validate the package offline; no renderer, authentication or media service."""

import argparse, datetime, importlib.util, io, json, unittest
from pathlib import Path
from common import ROOT


def check():
    spec = importlib.util.spec_from_file_location(
        "geomotion_offline_checks", ROOT / "tests/package_checks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(module)
    )
    return {
        "mode": "package_only",
        "checked_at": datetime.date.today().isoformat(),
        "passed": result.wasSuccessful(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "media_created": False,
        "renderer_launched": False,
        "media_services_called": False,
        "checks": stream.getvalue(),
        "not_tested": [
            "Actual acceptance in the user's Claude plugin/Skill upload UI",
            "Claude CLI plugin validation/loading",
            "Live Google AI Studio or Gemini API speech/models/voices",
            "Actual speech emotion/pronunciation/consistency",
            "Alignment against accepted narration",
            "Media rendering or end-to-end export in this revision",
            "Client-side discovery/execution in separately installed Claude Code/Codex/Antigravity",
        ],
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", help="Optional JSON validation report; no media output")
    a = ap.parse_args()
    r = check()
    out = json.dumps(r, ensure_ascii=False, indent=2)
    if a.report:
        Path(a.report).write_text(out + "\n", encoding="utf-8")
    print(out)
    raise SystemExit(0 if r["passed"] else 2)
