# GeoMotion Thai — install and invoke

## Current delivery: source package only

This package reuses the previous implementation and reusable resources. Installation and validation do not create media or connect to Google. No new sample clip, narration or render is required. The archive excludes previous MP4/WAV outputs and rendered project/frame directories. Existing icon PNGs, reference images, fonts and the model library remain reusable assets.

For the Claude **Upload plugin** screen, use `GeoMotion_Thai_Claude_Plugin.zip` directly. For a single Skill upload or local adapters, use the corrected `GeoMotion_Thai_Kit.zip`. See [archive layouts](platforms.md#upload-archives). For local Skill installation, unzip the portable Kit and open the `geomotion-thai` folder. Installation itself only copies files. The complete offline checker uses the declared Python dependencies in `requirements.txt`; install them in the checking environment if missing. This does not connect Google or generate media. The portable entry point is `SKILL.md`. Read `platforms.md` for the exact target folder and the distinction between local clients and cloud/web clients.

```bash
python scripts/check_package.py
python scripts/geomotion.py doctor
python scripts/install_skill.py --platform claude --scope project --workspace /path/to/project
python scripts/install_skill.py --platform codex --scope project --workspace /path/to/project
python scripts/install_skill.py --platform antigravity --scope project --workspace /path/to/project
```

Installer commands above are dry-run plans. Add `--apply` to the chosen command to install into that local workspace. It copies the existing bundle and never renders or authenticates services. Existing destinations are protected; `--replace` archives the prior directory first. For personal installations use `--scope user`.

## Invocation examples

For maintenance (no media):

> ใช้ GeoMotion Thai ตรวจแพ็กเกจ โครงสร้าง และการตั้งค่า โดยยังไม่สร้างคลิปหรือเรียกบริการสร้างสื่อ

After the user actually wants a clip:

> ใช้ GeoMotion Thai สร้างคลิปเรื่อง [หัวข้อ] 60 วินาที แนวตั้ง 9:16 พากย์ไทยผู้ชายจริงจัง หนักแน่น ดุดัน จาก Google AI Studio ใส่ซับ Kanit สองสี แสดงธงในประเทศก่อนซูมสู่ภูมิประเทศ 3D

> ใช้ GeoMotion Thai สร้างคลิปจากบทที่แนบ แนวนอน 16:9 ใช้ภาพโลโก้ที่แนบเป็นลายน้ำขวาบน กว้าง 10% ทึบ 70% จับภาพและซับตามเสียงจริง

Claude Code uses `/geomotion-thai`, Codex uses `$geomotion-thai` (or its skill selector), and current Antigravity App/CLI supports `/geomotion-thai`; inspect IDE discovery for its installed version. Mentioning the name in normal language also lets the agent select the Skill when discovery is supported.

## Later production workflow — only after a clip request

Install Python 3.11+, Blender 4.2–4.3 and FFmpeg/ffprobe with libass on the producing machine. Install `requirements.txt` (or the previously tested `requirements-tested.txt`). Pillow/RAQM and bundled Kanit are needed for Thai layout. A Skill folder itself does not install these binaries. Optional faster-whisper is for ASR candidates; reviewed manual timing is also supported.

```bash
python scripts/geomotion.py new /absolute/new-project --title '[หัวข้อ]'
# For 16:9 use new ... --landscape; each aspect has independent camera keys.
```

`new` writes only editable JSON/text/service settings. Replace the template's example script, country/flag records, claims, coordinates, routes, both camera layouts and timeline for the requested topic. It is not a ready factual story.

Only now may the producing agent run:

```bash
python scripts/geomotion.py prepare /absolute/project/project.json --produce-media
# Generate accepted narration in the authorized Google AI Studio UI at this stage.
python scripts/audio_timeline.py ingest /absolute/project/project.json /absolute/studio-export.wav --model ACTUAL_MODEL --voice ACTUAL_VOICE --produce-media
# Listen, correct real cues/keyword anchors, then retime and review camera/event ends.
python scripts/audio_timeline.py retime /absolute/project/project.json --produce-media
python scripts/geomotion.py validate /absolute/project/project.json
python scripts/geomotion.py render /absolute/project/project.json --produce-media
python scripts/geomotion.py compose /absolute/project/project.json --produce-media
python scripts/geomotion.py qc /absolute/project/project.json --produce-media
```

Without `--produce-media`, production entry points refuse before doing work. The flag is for the agent following an explicit clip request; it is not permission to start media generation during installation or package checks. `--visual-preview` does not bypass this gate. Final production still requires accepted Google audio, current hashes and reviewed timing. Deliver the future MP4, real-time SRT and editable project only after actual inspection.

For asset regeneration after an authorized clip request: `blender -b -P scripts/export_assets.py -- --produce-media`. Do not use this command during package maintenance. Existing model/PNG resources can simply be reused.

Read `connections.md` for deferred Google UI/API setup, and `test-status.md` for current checks and limitations.

## Rebuild upload packages without producing media

Run from the existing Skill directory. Outputs must be outside this directory. These commands only archive existing files; no Google connection, renderer, icon generation or audio synthesis is performed.

```bash
python scripts/build_package.py /absolute/output/GeoMotion_Thai_Kit.zip --kind skill
python scripts/build_package.py /absolute/output/GeoMotion_Thai_Claude_Plugin.zip --kind claude-plugin
python scripts/build_package.py /absolute/output/GeoMotion_Thai_Kit.zip --kind skill --check-only
python scripts/build_package.py /absolute/output/GeoMotion_Thai_Claude_Plugin.zip --kind claude-plugin --check-only
```

Every file must stay within the archive's one top-level directory. Do not add a checksum/readme as a sibling of that directory. The builder includes and verifies checksums internally.
