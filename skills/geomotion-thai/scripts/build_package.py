"""Build upload archives from existing files only; never generates media."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
NAME = "geomotion-thai"
MEDIA_OUTPUTS = {".mp4", ".mov", ".wav", ".mp3", ".aac", ".flac", ".srt", ".ass"}


def validate_archive(path, kind):
    """Check exact upload layout and all checksums without extracting files."""
    if kind not in {"skill", "claude-plugin"}:
        raise ValueError("Unknown archive kind")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if archive.testzip() or len(names) != len(set(names)):
            raise ValueError("Corrupt ZIP or duplicate entries")
        for name in names:
            parts = PurePosixPath(name)
            if (
                parts.is_absolute()
                or ".." in parts.parts
                or "\\" in name
                or len(parts.parts) < 2
                or parts.parts[0] != NAME
            ):
                raise ValueError("All files must be inside the top-level folder")
            if parts.suffix.lower() in MEDIA_OUTPUTS:
                raise ValueError("Rendered/audio outputs are excluded")
        prefix = f"{NAME}/"
        if kind == "claude-plugin":
            manifest = json.loads(archive.read(prefix + ".claude-plugin/plugin.json"))
            if manifest.get("name") != NAME or not manifest.get("description"):
                raise ValueError("Plugin manifest requires name and description")
            if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
                raise ValueError("Plugin version must use semantic versioning")
            prefix += f"skills/{NAME}/"
        raw = archive.read(prefix + "SKILL.md").decode("utf-8")
        if not raw.startswith("---\n") or f"name: {NAME}" not in raw.split("---", 2)[1]:
            raise ValueError("Missing Skill name/frontmatter")
        checksum_path = f"{NAME}/MANIFEST.sha256"
        listed = set()
        for line in archive.read(checksum_path).decode("utf-8").splitlines():
            digest, name = line.split("  ", 1)
            if (
                name in listed
                or hashlib.sha256(archive.read(name)).hexdigest() != digest
            ):
                raise ValueError("Checksum mismatch")
            listed.add(name)
        if listed != set(names) - {checksum_path}:
            raise ValueError("Incomplete checksum manifest")
    return {"archive": str(path), "kind": kind, "files": len(names), "valid": True}


def build(output, kind="skill"):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Write output outside the source Skill directory")
    if kind not in {"skill", "claude-plugin"}:
        raise ValueError("Unknown archive kind")
    prefix = f"{NAME}/"
    if kind == "claude-plugin":
        prefix += f"skills/{NAME}/"
    entries = {}
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(
            part in {"__pycache__", ".git", ".venv", "node_modules"}
            or part.startswith(".env")
            for part in rel.parts
        ):
            continue
        if path.suffix in {".pyc", ".blend1", ".zip", ".skill", ".plugin"}:
            continue
        if path.suffix.lower() in MEDIA_OUTPUTS or rel.name == "MANIFEST.sha256":
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink is not allowed: {rel}")
        data = path.read_bytes()
        if path.suffix in {".py", ".md", ".json", ".yaml", ".yml", ".txt"}:
            if re.search(
                rb"AIza[0-9A-Za-z_-]{35}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                data,
            ):
                raise ValueError(f"Secret detected: {rel}")
        entries[prefix + rel.as_posix()] = data
    if kind == "claude-plugin":
        entries[f"{NAME}/.claude-plugin/plugin.json"] = (
            ROOT / "config/claude-plugin.json"
        ).read_bytes()
    checksums = "".join(
        hashlib.sha256(data).hexdigest() + "  " + name + "\n"
        for name, data in sorted(entries.items())
    )
    entries[f"{NAME}/MANIFEST.sha256"] = checksums.encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    return validate_archive(output, kind)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output", type=Path)
    ap.add_argument("--kind", choices=["skill", "claude-plugin"], default="skill")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    action = validate_archive if args.check_only else build
    print(json.dumps(action(args.output, args.kind), ensure_ascii=False, indent=2))
