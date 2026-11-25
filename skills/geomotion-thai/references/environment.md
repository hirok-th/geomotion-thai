# Environment and execution boundaries

Current validation runs locally in package-only mode. `geomotion.py doctor` checks Python package availability, executable paths, font presence, RAQM availability and non-secret key presence. By default it does not launch Blender/FFmpeg or connect to services. Optional `--probe-binaries` only inspects local version/filter information; it does not render.

The existing backend targets Python 3.11+, Blender 4.2–4.3 and FFmpeg/ffprobe with libass. Dependencies and previously tested versions are in requirements files. Availability on this host does not install them in another client. Claude Code/Antigravity engines are not invoked during package validation. Browser/UI sessions and API permissions are separate from the shared SKILL.md format.

The retained renderer produces measured DEM geometry and perspective with layered objects. Its stylized materials and simplified models differ from the supplied photoreal references. Fine administrative masks, city-level DEM and missing rivers need appropriate sourced data before a specific production. No such data retrieval or scene generation occurs during installation/checks.
