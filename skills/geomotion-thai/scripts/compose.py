"""Compose Kanit ASS/SRT, tracked labels, original procedural effects, watermark.
Final export requires actual reviewed Google narration. Preview is visibly marked.
"""

import argparse, json, subprocess, wave, math, re, os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, features
from pythainlp.tokenize import word_tokenize
from execution_policy import production_only, enable_cli_production

from common import ROOT, read, write, digest, probe
from validate_project import validate


def ass_time(t):
    cs = round(t * 100)
    return f"{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}"


def srt_time(t):
    ms = round(t * 1000)
    return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"


def safe(s):
    return s.replace("\\", "").replace("{", "").replace("}", "")


def wrap(text, font, maxwidth):
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for token in word_tokenize(paragraph, engine="newmm", keep_whitespace=True):
            if font.getlength(line + token) > maxwidth and line:
                lines.append(line.strip())
                line = token.lstrip()
            else:
                line += token
        if line:
            lines.append(line.strip())
    if len(lines) > 2:
        raise ValueError(
            "Subtitle requires >2 lines; split cue at meaningful speech pause: " + text
        )
    return lines


@production_only
def make_subtitles(p, preview):
    c = read(p)
    b = p.parent
    t = read(b / c["timeline"])
    w, h = c["video"]["width"], c["video"]["height"]
    land = w > h
    cfg = c["subtitles"]
    size = cfg["font_size_landscape" if land else "font_size_portrait"]
    font = ImageFont.truetype(
        str(ROOT / "assets/fonts/Kanit-SemiBold.ttf"),
        size,
        layout_engine=ImageFont.Layout.RAQM,
    )
    if not features.check("raqm"):
        raise RuntimeError(
            "Pillow RAQM missing; install a build with HarfBuzz/Raqm before rendering Thai overlays"
        )
    sf = c["video"]["safe"]
    left = round(w * sf["left"])
    right = round(w * sf["right"])
    bottom = round(h * sf["bottom"])
    center = round((left + w - right) / 2)
    width = w - left - right
    cues = t.get("preview_cues", []) if preview else read(b / c["alignment"])["cues"]
    out = b / "build"
    out.mkdir(exist_ok=True)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Kanit SemiBold,{size},&H00FFFFFF,&H0000D7FF,&H00101820,&H70101820,0,0,0,0,100,100,0,0,1,3,1,2,{left},{right},{bottom},1
Style: Label,Kanit Medium,{40 if not land else 34},&H00FFFFFF,&H0000D7FF,&H00101820,&H80101820,0,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1
Style: Header,Kanit SemiBold,{52 if not land else 48},&H00FFFFFF,&H0000D7FF,&H00101820,&H80101820,0,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1
Style: Note,Kanit Medium,{25 if not land else 26},&H0037CCFF,&H0000D7FF,&H00101820,&H80101820,0,0,0,0,100,100,0,0,1,2,1,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    srt = []
    metrics = []

    def event(start, end, style, text, layer=1):
        events.append(
            f"Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}"
        )

    for i, q in enumerate(cues, 1):
        lines = wrap(q["text"], font, width * 0.94)
        plain = "\n".join(lines)
        colored = safe(plain)
        for kw in sorted(q.get("keywords", []), key=len, reverse=True):
            colored = colored.replace(kw, "{\\c&H00D7FF&}" + kw + "{\\c&HFFFFFF&}")
        colored = colored.replace("\n", "\\N")
        subtitle_y = h - bottom
        wide_intro = next(
            (
                e
                for e in t["events"]
                if e["kind"] == "country_intro"
                and e["start"] <= q["start"]
                and q["end"] <= e["start"] + e["phases"]["zoom_start"]
            ),
            None,
        )
        if not land and wide_intro:
            # In the portrait establishing layout, keep the hook above the country silhouette.
            subtitle_y = round(h * sf["top"] + 52 + 2 * size * 1.25 + 28)
        if "position_y_fraction" in q:
            subtitle_y = round(h * q["position_y_fraction"])
        if not h * sf["top"] + 2 * size <= subtitle_y <= h - bottom:
            raise ValueError("Caption position leaves the configured safe region")
        if cfg.get("enabled", True):
            event(
                q["start"],
                q["end"],
                "Sub",
                f"{{\\pos({center},{subtitle_y})\\fad(80,80)}}" + colored,
            )
        srt.append(f'{i}\n{srt_time(q["start"])} --> {srt_time(q["end"])}\n{plain}\n')
        metrics.append(
            {
                "cue": q["id"],
                "lines": len(lines),
                "max_width": max(font.getlength(x) for x in lines),
                "safe_width": width,
            }
        )
    titley = round(h * sf["top"])
    notey = titley - 44
    for q in c.get("screen_texts", []):
        event(
            q["start"],
            q["end"],
            "Header",
            f"{{\\pos({left},{titley})}}" + safe(q["text"]),
        )
    note = "ภาพตรวจงาน • ยังไม่มีเสียงพากย์" if preview else ""
    if note:
        event(0, t["duration"], "Note", f"{{\\pos({left},{notey})}}" + note)
    intro = next((e for e in t["events"] if e["kind"] == "country_intro"), None)
    reveal = (intro["start"] + intro["phases"]["tilt_end"]) if intro else 0
    schematic = (
        "เส้นทางจำลอง • "
        if any(r.get("schematic") for r in c.get("routes", []))
        else ""
    )
    event(
        reveal,
        t["duration"],
        "Note",
        f'{{\\pos({left},{titley+70})}}{schematic}ความสูงขยาย {c["geography"]["vertical_exaggeration"]} เท่า',
    )
    event(
        0,
        t["duration"],
        "Note",
        f"{{\\pos({left},{round(h*.86) if not land else round(h*.9)})}}Natural Earth • Mapzen / USGS / NOAA",
    )
    # Screen labels track camera projection; suppress offscreen/occluded labels, resolve collisions.
    anchors = read(out / "anchors.json")
    labfont = ImageFont.truetype(
        str(ROOT / "assets/fonts/Kanit-Medium.ttf"), 40 if not land else 34
    )
    fps = c["video"]["fps"]
    collisions = 0
    for f in range(1, round(t["duration"] * fps) + 1):
        tm = (f - 1) / fps
        used = []
        for place in c.get("places", []):
            if tm < place.get("show_at", 0):
                continue
            x, y, z = anchors[str(f)][place["id"]]
            text = place["label"]
            lw = labfont.getlength(text) + 20
            lh = 48
            if (
                z <= 0
                or x < left
                or x > w - right
                or y < titley + 160
                or y > h - bottom - 130
            ):
                continue
            x = max(left, min(w - right - lw, x + 17))
            y = max(titley + 145, min(h - bottom - 150, y - 40))
            for rect in used:
                if (
                    x < rect[2]
                    and x + lw > rect[0]
                    and y < rect[3]
                    and y + lh > rect[1]
                ):
                    y = rect[3] + 8
                    collisions += 1
            if y + lh > h - bottom - 100:
                continue
            used.append((x, y, x + lw, y + lh))
            event(
                tm,
                tm + 1 / fps,
                "Label",
                f"{{\\pos({round(x)},{round(y)})}}" + safe(text),
                0,
            )
    suffix = "PROVISIONAL" if preview else "Thai"
    (out / "captions.ass").write_text(
        header + "\n".join(events) + "\n", encoding="utf-8"
    )
    (out / f"captions.{suffix}.srt").write_text("\n".join(srt), encoding="utf-8")
    write(
        out / "typography_qc.json",
        {
            "font": "Kanit SemiBold + Kanit Medium",
            "font_sha256": digest(ROOT / "assets/fonts/Kanit-SemiBold.ttf"),
            "raqm": True,
            "thai_tokenizer": "pythainlp/newmm",
            "cues": metrics,
            "label_collision_adjustments": collisions,
            "safe_area": sf,
            "timing": "PROVISIONAL" if preview else "reviewed actual audio",
        },
    )
    return out / "captions.ass"


@production_only
def effects(project):
    c = read(project)
    b = project.parent
    t = read(b / c["timeline"])
    sr = 48000
    n = math.ceil(t["duration"] * sr)
    a = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(724)

    def add(tm, v, gain):
        start = round(tm * sr)
        end = min(n, start + len(v))
        a[start:end] += v[: end - start] * gain

    def noise(length):
        x = rng.standard_normal(int(length * sr))
        kernel = np.ones(12) / 12
        return np.convolve(x, kernel, "same")

    for e in t["events"]:
        if e["kind"] == "country_intro":
            tm = e["start"] + e["phases"]["wide"]
            x = np.arange(int(0.22 * sr)) / sr
            pop = np.sin(2 * np.pi * (800 * x - 1200 * x * x)) * np.exp(-24 * x)
            add(tm, pop, 0.09)
            x = np.linspace(0, 1, int(0.9 * sr))
            add(
                e["start"] + e["phases"]["zoom_start"],
                noise(0.9) * np.sin(np.pi * x) ** 2,
                0.17,
            )
        elif e["kind"] == "route":
            x = np.arange(int((e["end"] - e["start"]) * sr)) / sr
            if next(r for r in c["routes"] if r["id"] == e["route"])["mode"] == "rail":
                # Deliberately synthesized clacks; no claim of recorded train ambience.
                for tm in np.arange(e["start"], e["end"], 0.32):
                    v = noise(0.045) * np.exp(
                        -np.arange(int(0.045 * sr)) / (sr * 0.009)
                    )
                    add(tm, v, 0.035)
            else:
                add(
                    e["start"],
                    noise(0.9) * np.sin(np.linspace(0, np.pi, int(0.9 * sr))) ** 2,
                    0.07,
                )
    a = np.tanh(a)
    out = b / "build/effects.wav"
    with wave.open(str(out), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((a * 32767).astype("<i2").tobytes())
    return out


def ffpath(p):
    # Escaping for FFmpeg filter syntax, independent of shell quoting (shell is not used).
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "'\\''")


@production_only
def compose(project, preview=False):
    p = Path(project).resolve()
    b = p.parent
    c = read(p)
    v = validate(p, preview)
    if not v["valid"]:
        raise ValueError(json.dumps(v, ensure_ascii=False))
    record = b / "build/frame_render.json"
    if not record.exists():
        raise ValueError(
            "Frame render provenance missing; run the full render pipeline"
        )
    fr = read(record)
    if (
        fr.get("project_sha256") != digest(p)
        or fr.get("timeline_sha256") != digest(b / c["timeline"])
        or fr.get("scene_sha256") != digest(b / "build/GeoMotionThai.blend")
    ):
        raise ValueError(
            "Rendered frames are stale after project/timeline/scene changes; render again"
        )
    ass = make_subtitles(p, preview)
    sfx = effects(p)
    tl = read(b / c["timeline"])
    n = round(tl["duration"] * c["video"]["fps"])
    frames = b / "build/frames"
    missing = [
        i for i in range(1, n + 1) if not (frames / f"frame_{i:04d}.png").exists()
    ]
    if missing:
        raise ValueError(f"Missing render frames: {missing[:8]} ({len(missing)} total)")
    out = (
        b
        / "build"
        / ("GeoMotionThai_VISUAL_PREVIEW.mp4" if preview else "GeoMotionThai_FINAL.mp4")
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-filter_complex_threads",
        "2",
        "-framerate",
        str(c["video"]["fps"]),
        "-i",
        str(frames / "frame_%04d.png"),
        "-i",
        str(sfx),
    ]
    audio_index = None
    if not preview:
        cmd += ["-i", str(b / c["audio"]["file"])]
        audio_index = 2
    wm = c.get("watermark", {})
    wm_index = 3 if audio_index else 2
    if wm.get("enabled"):
        cmd += ["-loop", "1", "-i", str(b / wm["file"])]
    filters = [
        "[0:v]split[base][bright]",
        "[bright]colorlevels=rimin=0.6:gimin=0.55:bimin=0.6,gblur=sigma=5,colorchannelmixer=rr=0.16:gg=0.16:bb=0.08[glow]",
        "[base][glow]blend=all_mode=screen[map]",
    ]
    last = "map"
    if wm.get("enabled"):
        width = round(c["video"]["width"] * wm.get("width_fraction", 0.1))
        sf = c["video"]["safe"]
        x = round(c["video"]["width"] * sf["left"])
        y = round(c["video"]["height"] * sf["top"])
        pos = wm.get("position", "top-right")
        if "right" in pos:
            x = f'W-w-{round(c["video"]["width"]*sf["right"])}'
        if "bottom" in pos:
            y = f'H-h-{round(c["video"]["height"]*sf["bottom"])+180}'
        filters += [
            f'[{wm_index}:v]scale={width}:-1,format=rgba,colorchannelmixer=aa={wm.get("opacity",.7)}[logo]',
            f'[map][logo]overlay={x}:{y}:enable=\'between(t,{wm.get("start",0)},{wm.get("end",tl["duration"])})\'[wm]',
        ]
        last = "wm"
    subfilter = (
        f"subtitles=filename='{ffpath(ass)}':fontsdir='{ffpath(ROOT/'assets/fonts')}'"
    )
    filters.append(f"[{last}]" + subfilter + "[video]")
    if audio_index:
        filters += [
            f'[{audio_index}:a]loudnorm=I=-16:TP=-1.5:LRA=8,apad=whole_dur={tl["duration"]},asplit=2[voice][control]',
            "[1:a][control]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=220[ducked]",
            "[voice][ducked]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[audio]",
        ]
    else:
        filters.append("[1:a]anull[audio]")
    cmd += [
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[video]",
        "-map",
        "[audio]",
        "-t",
        str(tl["duration"]),
        "-c:v",
        "libx264",
        "-threads",
        "4",
        "-preset",
        "fast",
        "-crf",
        "19",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(out),
    ]
    log = b / "build/compose.log"
    with log.open("w") as f:
        subprocess.run(cmd, stdout=f, stderr=f, check=True)
    info = probe(out)
    write(
        b / "build/render_manifest.json",
        {
            "output": out.name,
            "mode": "VISUAL_PREVIEW_NO_NARRATION" if preview else "FINAL",
            "sha256": digest(out),
            "duration": info["format"]["duration"],
            "video": info["streams"][0],
            "audio_sha256": None if preview else digest(b / c["audio"]["file"]),
            "script_sha256": digest(b / c["script"]),
            "project_sha256": digest(p),
            "timeline_sha256": digest(b / c["timeline"]),
            "font_sha256": digest(ROOT / "assets/fonts/Kanit-SemiBold.ttf"),
            "watermark": wm,
            "limitations": (
                ["No narration; provisional cue times; synchronization untested"]
                if preview
                else []
            ),
        },
    )
    print(out)


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
    compose(a.project, a.visual_preview)
