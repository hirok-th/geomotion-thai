# Visual Style Guide — GeoMotion Thai

## Evidence log (25 November 2026)

| Reference | Access actually achieved | Use and limits |
|---|---|---|
| User `image.png`, 1672×941 | Full image inspected | Dark navy sea, saturated green relief, gold highlighted schematic shape, orange-gold curved arrows, red pins, white swept-wing aircraft, orange/white train with dark glazing, container ship. Visible warm light from upper right, deep crevice shadows, cloud bands and reflections. |
| User `image(1).png`, 1671×941 | Full image inspected | Same composition, plus a curved concrete dam, reservoir, white/glass modern city and smaller low buildings. Not evidence that the illustrated shape, mountain layout or rail route is a real geographic area. |
| [Facebook Reel](https://www.facebook.com/reel/1137303549015998) | Several moving frames observed after dismissing login overlay | Dark ocean and satellite-style land context. Observed Brazil filled green with white administrative borders/stars; subsequent China view with red country fill, gold stars and bright outline; short Thai subtitles in lower part. Country changes observed. Exact timing, full sound mix and entire clip not measured. Existing creator logo and satellite attribution belong to that reference and are not reusable brand assets. |
| [YouTube: 5noFJENobzE](https://www.youtube.com/shorts/5noFJENobzE) | Title/page metadata only; video readyState=0, time=0 | Title displayed “ทำไมพริกไทย ต้องมีคำว่า ไทย”. Player remained loading. No camera, icon, audio or transition analysis inferred. |
| [YouTube: kcCt7UK-OH0](https://www.youtube.com/shorts/kcCt7UK-OH0) | Title/page metadata only; video readyState=0, time=0 | Title displayed “ประเทศไทย กำลังเลื่อนไปทางตะวันออก”. No scene-level visual/audio analysis inferred. |

## Reusable direction

Use a saturated, dimensional geographic explainer. Retain real coastlines, borders, major river lines and measured relief. Use the supplied stills as color/light/silhouette targets, while treating the country/route imagery as illustrative.

| Element | Target |
|---|---|
| Ocean | Deep navy `#061C39`–`#073A60`, turquoise accent only near relevant coast/water |
| Land | Emerald/deep green; lighter altitude palette and directional hill shading |
| Focus | Gold `#FFCE50`, orange `#FF8C14`, selective red for urgency |
| Border | Narrow bright stroke, soft restrained halo; distinguish neighbors with dim strokes |
| Flag | Period-correct original flag colors within unchanged country polygon; readable hold before zoom |
| Vehicles | White/metal with orange accents, dark glazing, beveled edges; physically plausible orientation |
| Routes | Gold/orange curved or straight line; animated draw, arrowhead, clear destination |
| Labels | Kanit Medium/SemiBold, short Thai text, high contrast, restrained outline |
| Captions | White, black outline/shadow, yellow keyword; max two lines, bottom safe region |

Open wide, identify country with flag/name, hold, move continuously to target, fade flag, tilt into measured terrain, then reveal objects. Ease camera keys with clamped Bezier interpolation. Move objects at stable path speed and align headings to path tangents. Use small camera rotations only where they clarify geography. Pan/zoom across countries instead of unmotivated fast cuts.

Full frame composition must be assessed at 360 px wide. Keep key geometry outside right action controls and bottom caption/description area. Platform UI can change: safe regions are conservative editable defaults, not an official universal platform template.

## Difference between this implementation and target reference

The bundled Workbench renderer uses real triangular DEM geometry, actual perspective, material shading and cast shadows. It produces a clean stylized terrain look. It does not reproduce the attached images' photoreal vegetation, reflective sea, cloud volumes, sunset lighting, texture detail or dense urban modeling. Icon geometry is an original approximation. Highlight bloom is applied at composition. These differences must remain visible in reports; do not call it a photoreal match.

For greater realism, retain the same project data and create an Eevee/Cycles material/lighting adapter with licensed landcover/water textures and denser models. Benchmark that adapter before selecting it; it is not bundled or tested here. Never create random height noise to masquerade as real mountains.
