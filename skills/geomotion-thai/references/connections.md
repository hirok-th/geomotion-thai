# Deferred service connections

`config/services.example.json` is a non-secret example. No install/check command opens Google, verifies an account, lists remote voices/models, fetches DEM tiles or creates media. `geomotion.py new` copies it into the new project's `services.json` for later use. Keep the original package default unchanged.

| Connection | Default | What happens only after a clip request |
|---|---|---|
| Google AI Studio UI | Browser route; model/voice unset | Inspect the producing host's supported browser, authenticate securely if needed, inspect live model/voice choices, audition and lock a Thai male narrator |
| Gemini API | Disabled | Explain the separate API connection/key/quota/billing; obtain API-specific authorization before enabling the project setting |
| Map/DEM data | Bundled vector sources; no scene download at installation | Prepare region-specific measured DEM/cache only when the requested clip needs it |
| Local Blender/FFmpeg | No process is started by default package checks | Production commands launch them only under the explicit production gate |

The UI uses https://aistudio.google.com/generate-speech. A universal browser connector is not bundled: use the actual browser/handoff tools supplied by Claude/Codex/Antigravity or their host. Do not invent cookie access, private endpoints or universal tool names. UI authentication is unnecessary for building/installing this package.

For an authorized API route later, copy/edit the project's service file to set `gemini_api.enabled=true`, keep `base_url` on the official Google endpoint and keep `api_key_env` as an environment variable NAME (default `GEMINI_API_KEY`). Set the key securely outside project/Skill files. Set actual accessible model and voice in the project's audio settings after live discovery. Then:

```bash
python scripts/google_tts.py models --services /absolute/project/services.json --produce-media --allow-api
python scripts/google_tts.py voices --services /absolute/project/services.json --produce-media --allow-api
python scripts/google_tts.py speak --project /absolute/project/project.json --produce-media --allow-api
```

All API catalog/speech calls require both production activation and API authorization. Disabled connection, missing key, inaccessible model/voice or generation failure causes refusal; no other TTS provider is chosen. The adapter's current request schema is documented in `audio.md`; it has not been authenticated/synthesized in this package-only validation.

Do not include API keys, passwords, browser profiles, cookies, signed download URLs or populated secret files in exports. Store only public origins, non-secret settings, environment variable names and provenance hashes.
