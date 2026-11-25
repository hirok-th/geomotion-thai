# Project contract v1

Paths in a project are relative to `project.json`. Assets that belong to the skill resolve from the script location. Do not use secrets or absolute browser download URLs as configuration.

| File | Responsibility |
|---|---|
| `project.json` | Title/story date, video/safe regions, countries/flags, places, routes, camera layouts, narration preferences, caption/watermark settings, source claims |
| `services.json` | Deferred, non-secret project connection settings copied from the package example; API disabled by default |
| `script.th.txt` | Exact narration transcript; no stage directions that should not be spoken |
| `timeline.json` | Duration, event intervals and country intro phases; provisional demo cues only for previews |
| `alignment.json` | Actual audio/script SHA256, reviewed sentence cues and spoken keyword anchors |
| `audio/narration.wav` | Actual accepted Google narration |
| `audio/narration.provenance.json` | Provider/model/voice/source/hash/transcript hash, listening review flags |
| `data/scene_data.json` | Derived meshes and sampled routes/elevation; regenerate when geographic inputs change |
| `data/geodata_manifest.json` | DEM tile URLs/hashes, boundary source/hash, exaggeration and routing limitations |
| `build/` | Editable Blender scene, projected label anchors, ASS/SRT, effects, rendered frames/video and QC |

## Geography

`bbox=[west,south,east,north]`, `origin=[lon,lat]`, WGS84 degrees. Local X=east, Y=north, Z=up. `metres_per_unit=100000` keeps continental values manageable. Convert longitude with cos(origin latitude); this is a local equirectangular approximation, not a geodesic distance calculator. Camera width and object sizes are scene units.

`terrain_mode="dem"`, `dem_zoom=7`, `triangle_area_deg2=.002` for focus countries, `neighbour_triangle_area_deg2=.012`, `vertical_exaggeration=24` in demo. Always retain `source_note`. Select area/zoom based on scene scale and source resolution. Limits: non-wrapping bounds, |latitude|≤85°, ≤256 tile downloads per preparation. Split very large domains into scenes. Close urban or flood work needs higher-resolution source data and a suitable local CRS; the regional adapter is insufficient for hydraulic claims.

A country record has `iso` matching Natural Earth `ADM0_A3`, Thai `label`, and `flag={file,source_url,valid_from,valid_to,verified_for_story_date}`. The flag mask is the triangulated real boundary, including hole rings and parts; its XY shape stays unchanged while heights morph and material colors fade. Flag colors are sampled per triangle, so symbols/stripe edges have mesh-resolution limits. Inspect small symbols and increase mesh resolution before approving them. Historical flags/borders require explicit period sources and replacement geometry.

A place is `{id,label,lonlat:[lon,lat],icon,scale,show_at}`; elevation is derived, not handwritten. Optional field notes/source IDs should identify the chosen coordinate. A river is a real line dataset. A province polygon requires adding an administrative boundary layer to the builder; do not substitute a point marker while labeling it an area fill.

A route is `{id,coordinates:[[lon,lat],...],mode,vehicle,vehicle_scale,altitude_units,style,color,width,schematic,source}`. Two points produce a straight connection; three or more are spline-interpolated and resampled. `mode` is rail/sea/air, `style` solid/dashed. Optional `arrowhead` is triangle (default), chevron, diamond or double. Render symbols forward +Y; rotation follows tangent. `schematic=true` requires an on-screen disclosure. This pipeline does not solve real transport routing. Prevent sea curves crossing land and rail curves cutting ridges by supplying appropriate real control geometry and inspecting it.

## Timing

`timeline.duration` is actual accepted audio duration + a short tail in final production. Each event has `id,kind,start,end,anchor`. `kind=route` refers to a route ID. `kind=country_intro` refers to country ISO and has phases measured in seconds relative to event start:

- `wide`: duration of geographic establishing view.
- `flag_in`: duration of flag appearance after wide view.
- `hold`: recognition time before zoom; minimum 0.5 s.
- `zoom_start`: offset at/after wide + flag_in + hold.
- `flag_out_end`: flag has fully faded by this offset.
- `tilt_end`: relief reveal/tilt complete; must precede event end.

The project's camera layouts contain `{time,target:[lon,lat],target_z,width,tilt,azimuth}`. `portrait` and `landscape` are independent. Tilt is from vertical; azimuth rotates the direction. Event retiming does not automatically preserve a good camera composition: update all camera/event ends after rebuilding audio and visually inspect transitions. All movement interpolation is clamped Bezier; vehicle samples use linear transforms for constant-speed traversal.

`alignment.json` includes `audio_sha256,script_sha256,reviewed,duration,cues,anchors`. Cues contain `id,start,end,text,keywords`. Optional `position_y_fraction` overrides the safe subtitle baseline after visual review. The portrait wide-country hook defaults above the country silhouette; other cues use the lower safe region. Inspect that placement for every new geography. Anchors map the actual spoken keyword/event ID to seconds. Repeated words need unique anchor IDs (`th-first`, `th-return`) rather than ambiguous text. Final timeline needs matching `audio_sha256`, `timing_mode="reviewed_audio"`, `reviewed=true`. Hashes invalidate any timing from an older file. ASR candidate output is not reviewed alignment.

## Captions and watermark

Caption size depends on aspect; Kanit files are bundled. `enabled=false` removes spoken-caption dialogues but keeps labels and titles; SRT remains available. SRT does not carry Kanit or two-color styling. Literal ASS control characters are stripped from supplied text. Split cues at speech/meaning breaks if width exceeds two lines.

`watermark={enabled,user_requested,file,position,width_fraction,opacity,start,end}`. Both explicit instruction and original logo file are required. Defaults: top-right, .10 width, .7 opacity, [0,duration]. Positions top-left/top-right/bottom-left/bottom-right; all use safe margins. Overlay occurs after map bloom, stays fixed to the screen and preserves image aspect/alpha/colors. Inspect title/label/number collisions whenever enabled. Do not activate it for the two style reference attachments.
