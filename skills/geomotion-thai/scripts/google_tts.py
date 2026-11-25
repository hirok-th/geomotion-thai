"""Optional Gemini API adapter. Google AI Studio browser is the default.
API requests differ from the Studio UI and require explicit user consent first.
Never changes provider, model or voice after failure. No credentials are stored.
"""

import argparse, base64, json, os, wave, io
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from execution_policy import production_only, enable_cli_production

from common import ROOT, read, write, digest, duration

API = "https://generativelanguage.googleapis.com/v1beta/"


def load_api_settings(project=None, service_file=None):
    import re

    path = (
        Path(service_file).resolve()
        if service_file
        else ROOT / "config/services.example.json"
    )
    if project and not service_file:
        p = Path(project).resolve()
        c = read(p)
        candidate = p.parent / c.get("services", "services.json")
        if candidate.exists():
            path = candidate
    settings = read(path)["gemini_api"]
    if not settings.get("enabled"):
        raise RuntimeError(
            "Gemini API is disabled. Keep Google AI Studio UI as default; enable this project connection only after the user authorizes API use."
        )
    if settings.get("base_url") != API:
        raise ValueError("API origin must be the documented Google endpoint")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", settings.get("api_key_env", "")):
        raise ValueError(
            "Use an environment-variable name, never a key value in services.json"
        )
    return settings


@production_only
def call(path, body=None, settings=None):
    settings = settings or load_api_settings()
    key = os.environ.get(settings["api_key_env"])
    if not key:
        raise RuntimeError(
            "Set GEMINI_API_KEY securely in this process environment; never put it in project.json"
        )
    request = Request(
        settings["base_url"] + path,
        data=None if body is None else json.dumps(body, ensure_ascii=False).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        method="GET" if body is None else "POST",
    )
    try:
        with urlopen(request, timeout=180) as r:
            return json.load(r)
    except HTTPError as e:
        # Suppress raw error payloads, headers and URLs which may carry service diagnostics.
        raise RuntimeError(
            f"Google API returned HTTP {e.code}. Check account access/model/voice; no fallback was used."
        ) from None


@production_only
def catalog(path, field, settings=None):
    out = []
    token = None
    while True:
        q = (
            ("&" if "?" in path else "?")
            + urlencode(
                {("page_token" if path.startswith("voices") else "pageToken"): token}
            )
            if token
            else ""
        )
        response = call(path + q, settings=settings)
        out += response.get(field, [])
        token = response.get("nextPageToken") or response.get("next_page_token")
        if not token:
            return out


@production_only
def speak(project, allow, settings=None):
    if not allow:
        raise ValueError(
            "API differs from the requested Studio UI. Explain this and obtain permission; then pass --allow-api"
        )
    p = Path(project).resolve()
    c = read(p)
    a = c["audio"]
    model = a.get("model")
    voice = a.get("voice")
    if not model or not voice:
        raise ValueError("Choose model and voice only after checking live catalogs")
    settings = settings or load_api_settings(project)
    models = catalog("models?pageSize=1000", "models", settings)
    if not any(m["name"].removeprefix("models/") == model for m in models):
        raise ValueError("Requested TTS model not accessible in live catalog")
    voices = catalog("voices?page_size=1000", "voices", settings)
    names = {v.get("display_name", v.get("displayName")) for v in voices} | {
        v.get("id") for v in voices
    }
    if voice not in names:
        raise ValueError(
            "Requested voice not present in live catalog; no substitute selected"
        )
    if not model.startswith("gemini-3.8-"):
        raise ValueError(
            "Bundled adapter targets the current 3.8 Interactions schema. For other models review official docs and adapt explicitly."
        )
    transcript = (p.parent / c["script"]).read_text(encoding="utf-8")
    body = {
        "model": model,
        "input": [
            {
                "type": "user_input",
                "content": [
                    {
                        "type": "text",
                        "text": transcript,
                        "annotations": [
                            {"type": "speech_metadata", "style": a["direction"]}
                        ],
                    }
                ],
            }
        ],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    r = call("interactions", body, settings)
    parts = [
        part
        for st in r.get("steps", [])
        if st.get("type") == "model_output"
        for part in st.get("content", [])
        if part.get("type") == "audio"
    ]
    if not parts:
        raise ValueError("Google returned no audio")
    part = parts[-1]
    raw = base64.b64decode(part["data"])
    out = p.parent / a["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    mime = part.get("mime_type", part.get("mimeType", ""))
    if raw.startswith(b"RIFF"):
        out.write_bytes(raw)
    elif mime.startswith("audio/l16"):
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(raw)
    else:
        raise ValueError(
            "Unexpected Google audio format; review response without logging secrets"
        )
    write(
        out.with_suffix(".provenance.json"),
        {
            "provider": "Google Gemini API",
            "source": "https://aistudio.google.com/docs/speech-generation",
            "ui_equivalent": False,
            "api_authorized": True,
            "model": model,
            "voice": voice,
            "sha256": digest(out),
            "duration": duration(out),
            "transcript_sha256": digest(p.parent / c["script"]),
            "reviewed_pronunciation": False,
            "reviewed_performance": False,
        },
    )
    print(
        f"Created {out.name}. Listen and align the actual audio before final rendering."
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["models", "voices", "speak"])
    ap.add_argument("--project")
    ap.add_argument("--allow-api", action="store_true")
    ap.add_argument(
        "--services",
        help="Project-local service settings; default API connection stays disabled",
    )
    ap.add_argument(
        "--produce-media",
        action="store_true",
        help="Only after an explicit user clip request",
    )
    a = ap.parse_args()
    enable_cli_production(a.produce_media)
    if not a.allow_api:
        ap.error("API use requires --allow-api after explicit user authorization")
    settings = load_api_settings(a.project, a.services)
    if a.action == "speak":
        speak(a.project, a.allow_api, settings)
    else:
        path, field = (
            ("models?pageSize=1000", "models")
            if a.action == "models"
            else ("voices?language_code=th-TH&gender=male&page_size=1000", "voices")
        )
        print(json.dumps(catalog(path, field, settings), ensure_ascii=False, indent=2))
