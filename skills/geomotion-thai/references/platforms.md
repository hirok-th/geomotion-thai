# Supported local Skill installations

The portable core is a directory with `SKILL.md` (YAML `name` + `description`), scripts, references, assets and templates. Product discovery/configuration differs; rendering dependencies and browser permission are not supplied by the manifest.

Documentation checked 2026-11-25:

| Surface | Project skill folder | User/global folder | Explicit invocation |
|---|---|---|---|
| Claude Code | `.claude/skills/geomotion-thai/` | `~/.claude/skills/geomotion-thai/` | `/geomotion-thai` |
| Codex local | `.agents/skills/geomotion-thai/` | `~/.agents/skills/geomotion-thai/` | `$geomotion-thai` or name, according to client |
| Google Antigravity App/CLI/IDE | `.agents/skills/geomotion-thai/` | `~/.gemini/config/skills/geomotion-thai/` | `/geomotion-thai` on current App/CLI; inspect IDE UI |
| Current ChatGPT Work session | Managed personal skill catalog | Host-managed | Name GeoMotion Thai / select the installed skill |

Antigravity retains legacy `.agent/skills` support; do not choose that spelling as the default for a fresh installation. Older installations can differ. Check installed version and its live documentation before moving folders. Claude web/Cowork, Claude API containers and local Claude Code are distinct surfaces; copying files into a machine's home folder does not install an account skill on a web service.

`agents/openai.yaml` is optional Codex metadata. Claude/Antigravity can ignore it. No tool names, API credentials, browser selectors or cloud-specific handles appear in the common manifest. No platform-specific auto-permission, hooks or implicit shell expansion is required.

Local adapter, read-only plan first:

```bash
python scripts/install_skill.py --platform claude --scope project --workspace /path/to/project
python scripts/install_skill.py --platform codex --scope user
python scripts/install_skill.py --platform antigravity --scope project --workspace /path/to/project
```

Add `--apply` to copy after reviewing the destination. Existing folders are protected; `--replace` archives an existing folder first. This adapter is for local directories, not the current host's managed catalog. After moving/copying, run doctor with that copy's script path. Confirm skill discovery in the target product. This package-only revision checks installer destinations without executing any target client or rendering. The existing current-host Skill is updated separately. Actual Claude Code/Codex/Antigravity client discovery must be verified on the producing machine. No media generation or Google login is part of installation.

Official sources:

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Codex/local skill discovery](https://developers.openai.com/codex/skills)
- [Google Antigravity skills](https://antigravity.google/docs/skills)
- [Agent Skills specification](https://agentskills.io/specification)

## Upload archives

- `GeoMotion_Thai_Kit.zip`: portable single Skill. All entries, including `MANIFEST.sha256`, are inside `geomotion-thai/`; `geomotion-thai/SKILL.md` is the entry point. Use this for a Skill uploader, or extract for the local Codex/Antigravity/Claude Code adapters above.
- `GeoMotion_Thai_Claude_Plugin.zip`: Claude plugin wrapper. The single top-level `geomotion-thai/` contains `.claude-plugin/plugin.json` and `skills/geomotion-thai/SKILL.md`. Use this for the Claude **Upload plugin** page. Upload the ZIP itself, without repacking it. The manifest is generated from `config/claude-plugin.json`; code/resources are the same core Skill.

The original portable ZIP incorrectly placed `MANIFEST.sha256` outside the Skill folder. Claude reported "All files must be inside the top-level folder" after falling back to single-Skill validation because no plugin manifest was present. The fixed Skill ZIP moves the checksum file inside the folder. The separate Claude plugin ZIP includes a real plugin manifest rather than depending on fallback recognition.

Claude Code can test an extracted plugin locally with `claude --plugin-dir /absolute/path/to/geomotion-thai`; its plugin Skill command is `/geomotion-thai:geomotion-thai`. Ordinary local Skill installation continues to use `/geomotion-thai`. Cloud upload support and execution capabilities depend on the user's Claude surface/account. Upload validation does not install Blender/FFmpeg, enable Google authorization, or prove that end-to-end rendering works there. Neither archive is a browser extension or MCP service. Codex/Antigravity should use the portable Skill archive, not the Claude plugin wrapper.

Archive layouts and checksums are checked offline by `scripts/build_package.py` and the regression suite. No successful upload in the user's Claude account has been observed here. Official layout references: [Claude plugin manifest and standard directories](https://code.claude.com/docs/en/plugins/manifest-reference), [custom Skill ZIP structure](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

