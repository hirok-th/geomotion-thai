"""Portable local install adapter. Default is a read-only plan; add --apply to copy."""

import argparse, shutil, json, datetime
from pathlib import Path
from common import ROOT

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--platform", choices=["claude", "codex", "antigravity"], required=True
    )
    ap.add_argument("--scope", choices=["project", "user"], default="project")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--replace", action="store_true")
    a = ap.parse_args()
    if a.scope == "project":
        dest = (
            Path(a.workspace).resolve()
            / (".claude/skills" if a.platform == "claude" else ".agents/skills")
            / "geomotion-thai"
        )
    else:
        dest = (
            Path.home()
            / (
                {
                    "claude": ".claude/skills",
                    "codex": ".agents/skills",
                    "antigravity": ".gemini/config/skills",
                }[a.platform]
            )
            / "geomotion-thai"
        )
    if dest == ROOT or ROOT in dest.parents:
        raise SystemExit("Refuse recursive/self installation")
    print(
        json.dumps(
            {
                "source": str(ROOT),
                "destination": str(dest),
                "applied": a.apply,
                "note": "Local discovery only; not a cloud-account installation",
            },
            indent=2,
        )
    )
    if a.apply:
        if dest.exists():
            if not a.replace:
                raise SystemExit(
                    "Destination exists. Inspect it; use --replace only to archive and replace it."
                )
            backup = dest.with_name(
                dest.name
                + ".backup-"
                + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
            dest.rename(backup)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            ROOT,
            dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git", "*.blend1"),
        )
