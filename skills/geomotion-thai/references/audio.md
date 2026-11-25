# Google narration workflow — only after a clip request

Do not open/authenticate this service or generate a voice during package creation, installation or validation. Deferred production is not an unfinished packaging task. Read `connections.md` first.

## Preferred route: Google AI Studio UI

Use the authorized browser at [Generate speech](https://aistudio.google.com/generate-speech). Inspect visible live model and voice selections. Audition a Thai male narrator and retain the exact chosen model/voice for the project. A voice remembered from another session, including Riko, is not proof of availability today.

Guide delivery with serious, firm, controlled intensity, emotional pressure around reveals, clear Thai consonants/tones, and natural pauses. Put performance directions in the UI's direction controls; keep the exact transcript in the text field. Listen to a short sample before a long synthesis. Save the actual accepted export into `audio/` through the host-supported browser download/transfer route where available. If browser and execution machine differ, use the host's supported file bridge rather than cookies, private endpoints or undocumented fetches. Tell the user precisely if that bridge is unavailable.

Do not keep asking for manual audio downloads/reuploads as the normal workflow. A one-time user-supplied audio import is supported when the environment cannot transfer directly, but must be explained as a limitation. Never make up Google provenance for a sound file from another provider.

Use secure authentication prompts/handoff for login. Stop automation if credentials are rejected; do not retry remembered secrets. Keep credentials and account identifiers out of projects and logs. Earlier work reached a sign-in form without synthesis. This package-only revision does not request authentication; connect only for a future clip.

## Optional route: Gemini API (requires separate permission)

Before use, explain: “วิธีนี้จะสร้างเสียงผ่าน Gemini API ของ Google แทนหน้า Google AI Studio ต้องใช้ API key สิทธิ์รุ่น/เสียง โควตา และอาจมีค่าใช้จ่ายของ API แยกต่างหาก”. Only proceed if the user authorizes this difference. Never silently choose another TTS provider.

Read the current official [speech generation documentation](https://aistudio.google.com/docs/speech-generation), checked 2026-11-25. Current documentation covers Gemini 3.8 TTS and `/v1beta/interactions`, with text annotations for sustained speech style and WAV output. Model availability is account-specific; docs alone do not prove a live account can use it.

Set `GEMINI_API_KEY` in a secure process environment. The adapter sends it as an HTTP header, never in a URL or project. Do not print it or package `.env` files.

```bash
python scripts/google_tts.py models --services /absolute/project/services.json --produce-media --allow-api
python scripts/google_tts.py voices --services /absolute/project/services.json --produce-media --allow-api
# Choose actual accessible model and voice in project.json, after audition.
python scripts/google_tts.py speak --project /absolute/project/project.json --produce-media --allow-api
```

The adapter checks live models and voice catalog before synthesis. It supports the verified current 3.8 request schema and handles complete WAV vs explicit raw PCM; it refuses unexpected formats or inaccessible models/voices. It does not select a fallback. Older 2.5/3.1 preview APIs have different prompting/output conventions and must be adapted from their exact model documentation. Do not assume the 3.8 directions schema works with earlier models.

Live API synthesis remains untested in this release (no authorized API key). Only missing-key and no-permission guards were exercised. Listing voices does not establish perceived gender, Thai pronunciation quality or emotional performance; audition the actual sample.

## Alignment and review

Keep narration and script hashes. Optional local faster-whisper can propose sentence/word times from the actual waveform, but its Thai text and timestamps may be wrong. It is not a forced alignment guarantee. Compare against the exact script, listen and correct every important country/city/number/route anchor. If only phrase boundaries are reliable, align events to those boundaries and avoid claiming word precision.

For segment repairs, use the same voice/model/direction, retain context, compare timbre/loudness at joins, assemble the accepted waveform, then rebuild all cue/event timing against that assembled file. Never keep old subtitle times after regeneration.

Narration is normalized around -16 LUFS with peak headroom; synthesized effects are low-level and sidechain ducked under speech. Preview effects are original procedural cues, not external recordings. Add licensed music/ambience only when useful and record its provenance. Listen to the actual composed video before approving pronunciation, performance or synchronization.
