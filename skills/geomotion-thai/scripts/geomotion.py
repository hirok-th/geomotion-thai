#!/usr/bin/env python3
"""GeoMotion Thai project CLI. Run --help before using subcommands."""

import argparse, importlib.util, json, shutil, subprocess, sys, os
from pathlib import Path
from common import ROOT, read, write
from execution_policy import enable_cli_production


def doctor(probe_binaries=False):
    try:
        from PIL import features

        raqm = features.check("raqm")
    except ImportError:
        raqm = False
    report = {
        "python": sys.version.split()[0],
        "executables": {
            n: shutil.which(n)
            for n in [
                "blender",
                "ffmpeg",
                "ffprobe",
                "claude",
                "codex",
                "agy",
                "antigravity",
            ]
        },
        "packages": {
            n: bool(importlib.util.find_spec(n))
            for n in [
                "numpy",
                "PIL",
                "scipy",
                "shapely",
                "triangle",
                "pythainlp",
                "faster_whisper",
            ]
        },
        "thai_raqm": raqm,
        "fonts": {
            n: (ROOT / "assets/fonts" / n).is_file()
            for n in ["Kanit-Medium.ttf", "Kanit-SemiBold.ttf"]
        },
        "google_api_key_present": bool(os.environ.get("GEMINI_API_KEY")),
        "studio_browser": "must inspect authorized browser session; cannot infer login from an API key",
        "skill_root": str(ROOT),
        "default_mode": "package_only",
        "binaries_probed": probe_binaries,
    }
    if probe_binaries and report["executables"]["blender"]:
        report["blender_version"] = subprocess.check_output(
            ["blender", "--version"], text=True
        ).splitlines()[0]
    if probe_binaries and report["executables"]["ffmpeg"]:
        r = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True)
        report["libass"] = " subtitles " in r.stdout
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def new(dest, title, landscape):
    d = Path(dest).resolve()
    if d.exists():
        raise ValueError("Destination already exists; choose a new project directory")
    shutil.copytree(ROOT / "templates/project", d)
    c = read(d / "project.json")
    c["title"] = title
    if landscape:
        c["video"].update(
            width=1920,
            height=1080,
            safe={"left": 0.06, "right": 0.06, "top": 0.08, "bottom": 0.15},
        )
    shutil.copy2(ROOT / "config/services.example.json", d / "services.json")
    write(d / "project.json", c)
    print(str(d / "project.json"))
    print(
        "Template geography and narration are placeholders; no media was created. Replace script, claims, countries, coordinates, camera, routes and timeline for the new topic before production."
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    d = sub.add_parser("doctor")
    d.add_argument("--probe-binaries", action="store_true")
    q = sub.add_parser("new")
    q.add_argument("destination")
    q.add_argument("--title", default="หัวข้อใหม่")
    q.add_argument("--landscape", action="store_true")
    for name in ["prepare", "validate", "render", "compose", "qc"]:
        q = sub.add_parser(name)
        q.add_argument("project")
        q.add_argument("--visual-preview", action="store_true")
        if name != "validate":
            q.add_argument("--produce-media", action="store_true")
        if name == "render":
            q.add_argument("--still", type=int)
            q.add_argument("--frames")
            q.add_argument("--quality", type=int, default=100)
            q.add_argument("--threads", type=int, default=4)
            q.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()
    if a.command == "doctor":
        doctor(a.probe_binaries)
        return
    if a.command == "new":
        new(a.destination, a.title, a.landscape)
        return
    if a.command in {"prepare", "render", "compose", "qc"}:
        enable_cli_production(a.produce_media)
    p = Path(a.project).resolve()
    if a.command == "prepare":
        from prepare_geo import prepare

        prepare(p)
        return
    if a.command in ["validate", "render", "compose"]:
        from validate_project import validate

        v = validate(p, a.visual_preview)
        if not v["valid"]:
            print(json.dumps(v, ensure_ascii=False, indent=2))
            sys.exit(2)
        if a.command == "validate":
            print(json.dumps(v, ensure_ascii=False, indent=2))
            return
    if a.command == "render":
        if a.quality != 100 and not a.visual_preview:
            raise ValueError("Final rendering requires 100% native resolution")
        cmd = [
            "blender",
            "-b",
            "-t",
            str(a.threads),
            "-P",
            str(ROOT / "scripts/blender_scene.py"),
            "--",
            str(p),
            "--produce-media",
            "--quality",
            str(a.quality),
        ]
        if a.still:
            cmd += ["--still", str(a.still)]
        if a.frames:
            cmd += ["--frames", a.frames]
        if not a.still and not a.frames:
            cmd += ["--build-only"]
        subprocess.run(cmd, check=True)
        if not a.still and not a.frames:
            from render_frames import render

            render(p, a.workers, a.threads)
    elif a.command == "compose":
        from compose import compose

        compose(p, a.visual_preview)
    elif a.command == "qc":
        from qc import qc

        qc(p, a.visual_preview)


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        RuntimeError,
        FileNotFoundError,
        subprocess.CalledProcessError,
    ) as exc:
        print(
            json.dumps({"error": str(exc), "status": "blocked"}, ensure_ascii=False),
            file=sys.stderr,
        )
        sys.exit(2)
