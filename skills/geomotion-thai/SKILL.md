---
name: geomotion-thai
description: Provides on-demand Thai narrated geographic infographic animations with country flag masks, measured 3D terrain, moving routes and objects, Kanit captions, and optional explicitly requested watermarks. Use for GeoMotion Thai, animated maps, geographic/history/travel/transport/city/economy/disaster explainers, or reusable 2D–3D map videos from topics, scripts, or data. Package creation, installation and checks remain offline; produce media only after an explicit user clip request.
---

# GeoMotion Thai

## Execution scope — decide before doing any work

Default to **package-only** for creating, updating, installing, explaining or checking this Skill/plugin. Reuse existing code/resources. In this mode, only inspect files, validate syntax/configuration, copy text templates, and test local installation plans or disabled-action guards. Deliver the source package and platform instructions. Do **not** create sample clips, generate images/icons, download DEM for a scene, launch a renderer, synthesize/import audio, connect to Google, audition voices, request login, or create a demo. Deferred media production is not a blocker for delivering a package.

Enter production mode only when the user explicitly requests a clip/video in the current task. A package request, capability question, or installation request is not production authorization. Then apply the workflow below and pass `--produce-media` to production CLI commands. The future clip request supplies authorization for the necessary production steps; do not ask for a second generic confirmation. API substitution still needs the separate consent described below. A flag alone is not evidence of user intent: agents must first check the user's request.

Run `python scripts/check_package.py` for offline package validation. Run `python scripts/geomotion.py doctor` for local availability checks; it does not launch Blender/FFmpeg or connect services by default. For upload failures or repackaging, use the [platform archive layouts](references/platforms.md#upload-archives) and `scripts/build_package.py`; keep all entries inside the single top-level folder, and use the Claude wrapper only for plugin upload. Read [service settings](references/connections.md). `config/services.example.json` defaults to package-only; the Gemini API connection is disabled and contains no secret.

All following research, narration, asset regeneration, rendering and media delivery steps apply **only after a clip has been requested**. Safe `new` merely copies editable text/JSON templates; it does not create media.

Produce a reusable geographic story, then execute the bundled Python/Blender pipeline. Read [usage](references/usage.md) for commands, [platform adapters](references/platforms.md) when installing elsewhere, and [visual style](references/visual-style-guide.md) before every first production in a conversation. Resolve all paths relative to this skill folder; never assume a fixed home directory.

## 1. Inspect and plan

1. Run `python scripts/geomotion.py doctor`. Inspect actual browser/audio capabilities separately. Check Blender ≥4.2, FFmpeg with libass, dependencies, Kanit and Thai shaping. Read [environment](references/environment.md) for the tested setup and limitations. Never infer identical capabilities in Claude, Codex and Antigravity from their shared manifest format.
2. Open user references that are actually accessible. Record what was observed, what was metadata only, and what could not play. Never invent analysis of unseen frames, camera speed or narration. Treat attached visual references as style sources, not geographic evidence or watermark permission.
3. Research the new topic from primary sources. Save claims, dates, units, uncertainty and source URLs in project data. Verify country/administrative boundaries and any disputed/historical choices. Use measured DEM for height claims; do not hallucinate rivers, cities or mountains. Read [data and rights](references/data-and-rights.md).
4. Write a concise Thai hook, explanation and payoff. Use the duration requested for the future clip; measure actual narration rather than assuming a speaking rate. Do not create test clips during package maintenance. Choose story-specific content and geography; do not reuse demo facts for a different topic.
5. Ask only for missing decisions that block execution. Complete independent work while audio access is pending. Never claim a silent visual test meets the narrated-demo acceptance criteria.

## 2. Create an editable project

Copy `templates/project` into a NEW project with `geomotion.py new`. Replace `script.th.txt`, claims, country/flag records, places, routes, both camera layouts and `timeline.json`. Keep content and coordinates in these files, outside rendering code. Use [project contract](references/project-contract.md) for field definitions. Save the project and final deliverables to the host's persistent destination.

Use 1080×1920, 30 fps by default. For landscape, use `new --landscape` (1920×1080), separate camera keys and safe areas. Recompose rather than crop. Set map extent wide enough to cover every camera frustum; inspect render edges before full export. Do not use Web Mercator tiles as a linear latitude height grid; the preparer decodes and samples tile coordinates correctly.

## 3. Prepare geography and original assets

After a clip request, run `geomotion.py prepare PROJECT/project.json --produce-media`. This downloads/caches Terrarium tiles, records hashes, samples elevations, clips Natural Earth polygons, triangulates polygons with holes, and stores scene data. The DEM is measured; height exaggeration is explicit in project metadata and on screen. Keep data source notices with exported project/video descriptions.

Use `assets/icons/GeoMotion_Objects.blend` and original layered generators in `scripts/models.py`. Consult [asset comparison](references/asset-comparison.md) and its comparison sheet before using them. These are stylized 3D approximations of the supplied reference silhouettes, not photoreal replicas. Regenerate or refine the model when the topic needs a different object; preserve distinct wheels, body, rails, shadow/wake, route and arrow layers. Do not reuse an unreviewed new asset as if it passed comparison.

Country introduction is mandatory on first mention:

1. Establish the country in a wide surrounding map.
2. Fill its exact polygon with the correct period flag; show a bright restrained border and Thai country name.
3. Hold recognition long enough to read (at least 0.5 seconds; normally 1–2 seconds after flag appearance).
4. Zoom continuously toward the target.
5. Fade flag colors into terrain during the zoom, keeping polygon XY coordinates unchanged.
6. Reveal measured height and tilt perspective smoothly.
7. Reveal topic-specific city, route and object layers.

Represent these phases explicitly in a `country_intro` event. Keep camera keyframes synchronized to the phase times. For subsequent countries, add new first-mention events; returning mentions may shorten them. For cities/provinces/rivers use verified point/line/area data at an appropriate scale. The bundled renderer handles country polygons and point labels; add real admin-area geometry to the scene builder for a province fill, or clearly use a point marker—never pass one off as an area mask.

Routes support straight/two-point or curved/multi-point coordinates, solid/dashed paths, a drawing arrowhead, and vehicles with heading from path tangent. Use the same densified path for vehicle and route. Check ground contact, sea level and symbolic flight clearance. Label illustrative routes as schematic; obtain real routing geometry before claiming an actual railway/road/shipping alignment.

## 4. Generate and listen to Google narration

Read [audio workflow](references/audio.md). Default to the authorized Google AI Studio UI at `https://aistudio.google.com/generate-speech`. Inspect live models and voices; audition a Thai male voice and lock it for all segments. Verify any user-named voice exists; never silently replace it.

Direct the narrator: “เล่าด้วยน้ำเสียงจริงจัง หนักแน่น ดุดันอย่างมีชั้นเชิง มีพลังและความน่าเชื่อถือ ถ่ายทอดอารมณ์ตามเหตุการณ์ ออกเสียงไทยชัดเจน เน้นคำสำคัญ และเว้นจังหวะอย่างเป็นธรรมชาติ”. Increase pressure at key reveals, preserve comfortable loudness and natural pauses. Listen to the actual output. Repair only failed segments with the same model/voice/direction.

Use a host-supported direct download into the project; do not repeatedly ask the user to download/re-upload. Use secure account handoff for sign-in. Never read cookies, recover tokens, reuse remembered credentials or embed secrets in files. A login failure is a blocker, not permission to use a different TTS service.

An OPTIONAL Gemini API adapter is provided. Explain that it uses a separate API connection, key, model access/quota and potentially billing rather than the Studio browser UI. Obtain permission BEFORE using it. Then use live catalog discovery and `google_tts.py speak --project PROJECT/project.json --produce-media --allow-api`. No model/voice fallback occurs on failure. Do not call the API path “AI Studio UI”. The API request implementation has not been live synthesized in this environment.

## 5. Bind visuals and subtitles to actual audio

Ingest the actual Studio export with `audio_timeline.py ingest`; record model, voice, source, file hash and script hash. Listen and mark pronunciation/performance reviewed in provenance only after checking them.

Create actual sentence cues and spoken keyword anchors. Optional faster-whisper creates ASR candidates, not forced alignment. Correct candidates by listening; use `alignment.example.json` as the contract. Each cue needs actual start/end; each event needs a reviewed keyword anchor. Run `audio_timeline.py retime` to bind events; update camera keys, recognition holds and event ends, inspect the actual audio, then mark the timeline reviewed. Never use proportional text-length timing as verified synchronization. A script OR audio hash change invalidates alignment and final export.

Use Kanit Medium/SemiBold from `assets/fonts`. Compose actual ASS with white text, black outline, subtle shadow, yellow keywords, ≤2 meaningful lines and Thai tokenization. Burn the same font into video; deliver separate SRT (SRT has no font/color styling). `subtitles.enabled=false` disables subtitle cues while retaining informational labels. Use actual narration cues for the final SRT. Demo `PROVISIONAL.srt` is explicitly not audio synchronized.

## 6. Render, inspect, deliver

1. Validate final project. A missing Google narration, stale hash or unreviewed timeline MUST block final export. Use `--visual-preview` only for an explicitly labeled visual test.
2. Render selected stills first, including wide flag, midfade, tilted terrain, route travel and final frame. Inspect camera framing and label collisions before rendering all frames.
3. Render with `geomotion.py render PROJECT/project.json --produce-media`. The Blender source has editable country, terrain, water, river, object, route, rail and camera layers. Use the supplied .blend or regenerate from configuration.
4. Compose using `geomotion.py compose PROJECT/project.json --produce-media`: Kanit captions/labels, original procedural whoosh/pop/clacks, normalized narration and ducked effects. The built-in effects are synthesized cues, not recordings. Add licensed contextual ambience/music when needed and record its source; do not overpower narration.
5. Enable watermark ONLY when the user has supplied/identified the original logo AND explicitly requested its use as watermark. Require `enabled=true`, `user_requested=true`, and a valid original file. Default: top-right, 10% frame width, 70% opacity, full duration, safe margins, screen-locked. Keep source color/aspect/alpha and inspect collisions with title, numbers, labels and captions. Mere reference attachments never activate watermark.
6. Run `geomotion.py qc PROJECT/project.json --produce-media`, inspect actual decoded frames and contact sheet; listen to the final export through available media tools. Check duration/dimensions/frame count, Kanit font selection, Thai marks/line breaks, flag mask/fade, actual parallax/relief, route direction, vehicle heading/contact, subtitle/keyword timing and mobile safety. Check a landscape render separately when requested. Do not equate automated checks with listening/visual approval.
7. Deliver MP4, SRT, editable project (JSON, script, data/provenance, .blend), reusable assets, and a test report. Identify tested features and concrete remaining blockers. Keep API keys, credentials, browser state and signed links out of all packages.

Read [test status](references/test-status.md) for the current package-only checks and explicit untested areas. Package delivery does not require narration, a demo or service authentication. For a later clip, never claim speech/synchronization/render acceptance until that actual production output is inspected.
