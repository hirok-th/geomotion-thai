"""Audio ingestion and ASR candidate timing. Never treats estimates as alignment."""

import argparse, json, shutil, re, subprocess
from pathlib import Path
from execution_policy import production_only, enable_cli_production

from common import read, write, digest, duration


@production_only
def ingest(project, source, model, voice):
    p = Path(project).resolve()
    c = read(p)
    src = Path(source).resolve()
    out = p.parent / c["audio"]["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    normalized = out.with_name(out.stem + ".normalized.wav") if src == out else out
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(src),
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(normalized),
        ],
        check=True,
    )
    if normalized != out:
        normalized.replace(out)
    write(
        out.with_suffix(".provenance.json"),
        {
            "provider": "Google AI Studio",
            "source": "https://aistudio.google.com/generate-speech",
            "model": model,
            "voice": voice,
            "sha256": digest(out),
            "duration": duration(out),
            "transcript_sha256": digest(p.parent / c["script"]),
            "reviewed_pronunciation": False,
            "reviewed_performance": False,
        },
    )
    # Existing cues keep old hash; final validation rejects until reviewed against new audio.
    print(
        f"Imported {out.name} ({duration(out):.3f}s). Existing alignment must be renewed."
    )


@production_only
def candidate(project, model):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit(
            "Install optional faster-whisper, or enter manual cues after listening to actual narration."
        )
    p = Path(project).resolve()
    c = read(p)
    audio = p.parent / c["audio"]["file"]
    asr = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = asr.transcribe(
        str(audio), language="th", word_timestamps=True, vad_filter=True
    )
    cues = []
    words = []
    for seg in segments:
        cues.append(
            {
                "id": f"s{len(cues)+1}",
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
                "keywords": [],
            }
        )
        words += [
            {
                "word": w.word,
                "start": w.start,
                "end": w.end,
                "probability": w.probability,
            }
            for w in (seg.words or [])
        ]
    write(
        p.parent / "alignment.candidate.json",
        {
            "audio_sha256": digest(audio),
            "script_sha256": digest(p.parent / c["script"]),
            "method": "ASR candidate; not forced alignment",
            "reviewed": False,
            "duration": duration(audio),
            "cues": cues,
            "words": words,
        },
    )
    print(
        "Candidate only. Compare with script, listen, correct boundaries and keyword anchors, then save alignment.json with reviewed=true."
    )


@production_only
def retime(project):
    p = Path(project).resolve()
    c = read(p)
    a = read(p.parent / c["alignment"])
    audio = p.parent / c["audio"]["file"]
    if (
        not a.get("reviewed")
        or a["audio_sha256"] != digest(audio)
        or a["script_sha256"] != digest(p.parent / c["script"])
    ):
        raise ValueError(
            "Alignment must be reviewed against current audio AND script hashes"
        )
    t = read(p.parent / c["timeline"])
    old = {q["id"]: q for q in a["cues"]}
    anchors = a.get("anchors", {})
    for e in t["events"]:
        if "anchor" not in e:
            raise ValueError(
                "Every visual event requires a reviewed spoken keyword anchor"
            )
        if e["anchor"] not in anchors:
            raise ValueError("Missing reviewed keyword " + e["anchor"])
        start = anchors[e["anchor"]]
        length = e["end"] - e["start"]
        e["start"] = start
        e["end"] = start + length
    t["audio_sha256"] = digest(audio)
    t["duration"] = duration(audio) + c.get("tail_seconds", 0.5)
    t["timing_mode"] = "reviewed_audio"
    t["reviewed"] = False
    write(p.parent / c["timeline"], t)
    print(
        "Events moved to recorded keyword anchors. Review country holds, camera keys and event ends before setting timeline.reviewed=true."
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="action", required=True)
    x = sub.add_parser("ingest")
    x.add_argument("project")
    x.add_argument("source")
    x.add_argument("--model", required=True)
    x.add_argument("--voice", required=True)
    x = sub.add_parser("candidate")
    x.add_argument("project")
    x.add_argument("--model", default="small")
    x = sub.add_parser("retime")
    x.add_argument("project")
    for parser in sub.choices.values():
        parser.add_argument("--produce-media", action="store_true")
    a = ap.parse_args()
    enable_cli_production(a.produce_media)
    if a.action == "ingest":
        ingest(a.project, a.source, a.model, a.voice)
    elif a.action == "candidate":
        candidate(a.project, a.model)
    else:
        retime(a.project)
