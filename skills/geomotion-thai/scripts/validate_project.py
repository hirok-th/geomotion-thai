"""Fail-closed checks for geographic inputs, final audio, cue timing and assets."""

import argparse, json, sys, math
from pathlib import Path
from common import ROOT, read, digest, duration, geography_signature


def validate(project, preview=False):
    p = Path(project).resolve()
    b = p.parent
    c = read(p)
    t = read(b / c["timeline"])
    errors = []
    warnings = []

    def check(v, msg):
        if not v:
            errors.append(msg)

    v = c["video"]
    check(v["width"] % 2 == 0 and v["height"] % 2 == 0, "Frame dimensions must be even")
    check(v["fps"] > 0, "FPS must be positive")
    check(t["duration"] > 0, "Duration must be positive")
    if (b / "data/scene_data.json").exists():
        check(
            geography_signature(c)
            == geography_signature(read(b / "data/scene_data.json")["config"]),
            "Geographic configuration changed; run prepare again",
        )
    g = c["geography"]
    check(
        g["terrain_mode"] == "dem",
        "Real terrain requires measured DEM; procedural noise is not elevation",
    )
    check(g["vertical_exaggeration"] >= 1, "Exaggeration must be >=1")
    check(bool(g.get("source_note")), "Record data source and exaggeration")
    font = ROOT / "assets/fonts/Kanit-SemiBold.ttf"
    check(font.exists(), "Kanit SemiBold missing")
    for e in t["events"]:
        check(
            0 <= e["start"] < e["end"] <= t["duration"],
            f'Event {e["id"]}: invalid bounds',
        )
        if e["kind"] == "country_intro":
            q = e["phases"]
            keys = ["wide", "flag_in", "hold", "zoom_start", "flag_out_end", "tilt_end"]
            check(all(k in q for k in keys), "Country introduction missing phases")
            if all(k in q for k in keys):
                check(
                    q["wide"] > 0 and q["flag_in"] > 0 and q["hold"] >= 0.5,
                    "Country needs perceptible wide/flag/hold",
                )
                check(
                    q["zoom_start"] >= q["wide"] + q["flag_in"] + q["hold"],
                    "Zoom precedes recognition hold",
                )
                check(
                    q["zoom_start"]
                    < q["flag_out_end"]
                    <= q["tilt_end"]
                    <= e["end"] - e["start"],
                    "Flag fade/tilt order invalid",
                )
    for country in c.get("countries", []):
        check(
            any(
                e["kind"] == "country_intro" and e["country"] == country["iso"]
                for e in t["events"]
            ),
            "Missing first-country introduction",
        )
        flag = country["flag"]
        check(
            bool(flag.get("valid_from")) and bool(flag.get("source_url")),
            "Flag needs date and source",
        )
        check(
            flag.get("verified_for_story_date", False),
            "Flag has not been checked for story date",
        )
        if (b / "data/scene_data.json").exists():
            d = read(b / "data/scene_data.json")
            check(
                any(x["iso"] == country["iso"] for x in d["objects"]),
                "Country not in prepared extent",
            )
            check((b / flag["file"]).exists(), "Flag file missing")
    for r in c.get("routes", []):
        check(r.get("source") is not None, "Route needs source or schematic disclosure")
        if r.get("schematic"):
            warnings.append("Route " + r["id"] + " is schematic, not navigational")
    wm = c.get("watermark", {})
    if wm.get("enabled"):
        check(
            wm.get("user_requested") is True and bool(wm.get("file")),
            "Watermark requires logo AND explicit user instruction",
        )
        check(
            (b / (wm.get("file") or "__missing__")).is_file(),
            "Watermark original file missing",
        )
        check(0 < wm.get("opacity", 0.7) <= 1, "Invalid watermark opacity")
        check(
            0 <= wm.get("start", 0) < wm.get("end", t["duration"]) <= t["duration"],
            "Watermark time out of range",
        )
    if not preview:
        audio = b / c["audio"]["file"]
        check(audio.exists(), "Narration absent; final export blocked")
        check((b / c["alignment"]).exists(), "Reviewed audio alignment absent")
        if audio.exists():
            sha = digest(audio)
            provfile = audio.with_suffix(".provenance.json")
            check(provfile.exists(), "Audio provenance missing")
            if provfile.exists():
                pr = read(provfile)
                check(
                    pr.get("provider") in ["Google AI Studio", "Google Gemini API"],
                    "Narration provider must be Google",
                )
                check(pr.get("sha256") == sha, "Audio provenance stale")
                check(
                    pr.get("transcript_sha256") == digest(b / c["script"]),
                    "Script changed after narration",
                )
                check(
                    pr.get("reviewed_performance") and pr.get("reviewed_pronunciation"),
                    "Listen and review voice performance/pronunciation",
                )
                if pr.get("provider") == "Google Gemini API":
                    check(
                        pr.get("api_authorized") is True,
                        "Gemini API substitution not authorized",
                    )
            if (b / c["alignment"]).exists():
                a = read(b / c["alignment"])
                check(
                    a.get("audio_sha256") == sha, "Alignment stale after audio change"
                )
                check(
                    a.get("script_sha256") == digest(b / c["script"]),
                    "Alignment stale after script change",
                )
                check(a.get("reviewed") is True, "Alignment not reviewed")
                last = 0
                for q in a["cues"]:
                    check(
                        last <= q["start"] < q["end"] <= duration(audio) + 0.1,
                        "Subtitle order/duration invalid",
                    )
                    check(q["text"].count("\n") < 2, "Subtitle exceeds two lines")
                    last = q["end"]
                check(
                    t.get("audio_sha256") == sha
                    and t.get("reviewed") is True
                    and t.get("timing_mode") == "reviewed_audio",
                    "Timeline not reviewed against current narration",
                )
                for e in t["events"]:
                    check(
                        e.get("anchor") in a.get("anchors", {}),
                        "Visual event lacks reviewed keyword anchor",
                    )
                    if e.get("anchor") in a.get("anchors", {}):
                        check(
                            abs(e["start"] - a["anchors"][e["anchor"]]) <= 1 / v["fps"],
                            "Visual event is not aligned to its reviewed keyword",
                        )
    else:
        warnings.append(
            "VISUAL PREVIEW: no claim of narrated, synchronized or completed production"
        )
    result = {
        "valid": not errors,
        "mode": "visual_preview" if preview else "final",
        "errors": errors,
        "warnings": warnings,
    }
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project")
    ap.add_argument("--visual-preview", action="store_true")
    a = ap.parse_args()
    r = validate(a.project, a.visual_preview)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(0 if r["valid"] else 2)
