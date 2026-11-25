"""Inspect actual exported media; leave listening/visual judgments explicitly pending."""

import argparse, json, subprocess, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from execution_policy import production_only, enable_cli_production

from common import ROOT, read, write, probe, digest


@production_only
def qc(project, preview=False):
    p = Path(project).resolve()
    b = p.parent
    c = read(p)
    t = read(b / c["timeline"])
    out = b / "build"
    video = out / (
        "GeoMotionThai_VISUAL_PREVIEW.mp4" if preview else "GeoMotionThai_FINAL.mp4"
    )
    info = probe(video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    errors = []
    if [vs["width"], vs["height"]] != [c["video"]["width"], c["video"]["height"]]:
        errors.append("Unexpected output dimensions")
    if abs(dur - t["duration"]) > 1 / c["video"]["fps"] + 0.02:
        errors.append("Unexpected output duration")
    expected = round(t["duration"] * c["video"]["fps"])
    actual = int(vs.get("nb_frames", 0))
    if actual != expected:
        errors.append("Frame count differs from timeline")
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    if r.returncode or r.stderr.strip():
        errors.append("Media decode failed: " + r.stderr[-200:])
    # Extract actual decoded frames, not source stills.
    times = [0.5, 2.5, 5.8, 8.6, 11, 15, 18.8, 23]
    samples = []
    for i, tm in enumerate(times):
        tm = min(tm, dur - 0.1)
        file = out / f"qc_frame_{i}.jpg"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-ss",
                str(tm),
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(file),
            ],
            check=True,
        )
        samples.append(Image.open(file).convert("RGB"))
    thumbw = 270 if vs["height"] > vs["width"] else 480
    thumbh = round(thumbw * vs["height"] / vs["width"])
    sheet = Image.new("RGB", (thumbw * 4, (thumbh + 36) * 2), (8, 19, 30))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(ROOT / "assets/fonts/Kanit-Medium.ttf"), 21)
    for i, im in enumerate(samples):
        im.thumbnail((thumbw, thumbh))
        x = (i % 4) * thumbw
        y = (i // 4) * (thumbh + 36)
        sheet.paste(im, (x, y + 36))
        d.text((x + 10, y + 4), f"{times[i]:.1f}s", font=font, fill="white")
    sheet.save(out / "QC_ContactSheet.jpg", quality=93)
    log = (out / "compose.log").read_text(errors="replace")
    fonts = [x for x in log.splitlines() if "fontselect:" in x]
    if c["subtitles"].get("enabled", True) and not any("Kanit" in x for x in fonts):
        errors.append("Kanit not confirmed by actual libass font selection")
    report = {
        "automated_pass": not errors,
        "errors": errors,
        "sha256": digest(video),
        "duration": dur,
        "dimensions": [vs["width"], vs["height"]],
        "fps": vs.get("avg_frame_rate"),
        "frames": actual,
        "expected_frames": expected,
        "audio_present": audio is not None,
        "font_selection": fonts,
        "visual_review": "pending human/agent inspection of decoded contact sheet and individual frames",
        "narration_and_sync_review": (
            "BLOCKED: Google AI Studio authentication"
            if preview
            else "pending listening to actual export"
        ),
        "mode": "VISUAL_PREVIEW" if preview else "FINAL",
        "output": str(video),
    }
    write(out / "qc_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project")
    ap.add_argument("--visual-preview", action="store_true")
    ap.add_argument(
        "--produce-media",
        action="store_true",
        help="Only after an explicit user clip request",
    )
    a = ap.parse_args()
    enable_cli_production(a.produce_media)
    qc(a.project, a.visual_preview)
