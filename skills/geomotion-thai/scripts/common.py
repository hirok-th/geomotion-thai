"""Shared project IO, media probing and deterministic hashing."""

import json, hashlib, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write(p, v):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def probe(p):
    return json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(p),
            ]
        )
    )


def duration(p):
    return float(probe(p)["format"]["duration"])


def load_project(path):
    p = Path(path).resolve()
    c = read(p)
    return p, c


def audio_fingerprint(c, base):
    a = c.get("audio", {})
    p = base / a.get("file", "audio/narration.wav")
    return digest(p) if p.exists() else None


def geography_signature(c):
    def strip(x):
        if isinstance(x, dict):
            return {
                k: strip(v)
                for k, v in x.items()
                if k not in ["sampled_xyz", "elevation_m"]
            }
        if isinstance(x, list):
            return [strip(v) for v in x]
        return x

    payload = strip(
        {k: c.get(k) for k in ["geography", "countries", "places", "routes"]}
    )
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
