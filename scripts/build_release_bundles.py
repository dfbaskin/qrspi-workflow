#!/usr/bin/env python3
"""Package the output of `ruler apply` into one .zip per AI tool.

    pnpm run ruler:apply
    python3 scripts/build_release_bundles.py 1.0.0

Writes into dist/: one archive per tool, a .sha256 beside each, a combined
SHA256SUMS.txt, and RELEASE_NOTES.md.

Archives are deterministic -- entries are sorted, and their timestamps, modes
and host system are fixed -- so identical content always hashes identically.
Text output is written as bytes with LF endings, so a SHA256SUMS.txt produced
on Windows still verifies with `sha256sum -c`.
"""

from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

# Paths `ruler apply` generates for each tool, relative to the repo root.
#
# Cursor, Copilot, Codex and Gemini all share the root AGENTS.md -- ruler does
# not write .cursor/rules/ or .github/copilot-instructions.md. Copilot's skills
# target is .claude/skills, because ruler maps its `claude` skills target to
# Claude Code, Copilot and KiloCode alike.
BUNDLES = [
    ("claude", "Claude Code", ["CLAUDE.md", ".claude/skills", ".claude/agents"]),
    ("cursor", "Cursor", ["AGENTS.md", ".cursor/skills", ".cursor/agents"]),
    ("copilot", "GitHub Copilot", ["AGENTS.md", ".claude/skills", ".github/agents"]),
    ("codex", "Codex CLI", ["AGENTS.md", ".agents/skills", ".codex/agents"]),
    ("gemini-cli", "Gemini CLI", ["AGENTS.md", ".gemini/settings.json", ".gemini/skills"]),
]

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# The zip format cannot represent anything earlier than 1980-01-01.
ZIP_DATE = (1980, 1, 1, 0, 0, 0)
UNIX_CREATE_SYSTEM = 3
FILE_MODE = 0o644


def write_text(target: Path, text: str) -> None:
    """Write UTF-8 with LF endings, whatever platform we are on."""
    target.write_bytes(text.encode("utf-8"))


def collect(paths: list[str]) -> list[tuple[str, Path]]:
    """Every file under `paths`, as (archive name, source path), sorted."""
    found: list[tuple[str, Path]] = []
    for entry in paths:
        source = ROOT / entry
        candidates = sorted(source.rglob("*")) if source.is_dir() else [source]
        for path in candidates:
            if not path.is_file() or path.name.endswith(".bak"):
                continue
            found.append((path.relative_to(ROOT).as_posix(), path))
    return sorted(set(found))


def build_zip(target: Path, files: list[tuple[str, Path]]) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for arcname, source in files:
            info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
            # Pin the host system too: zipfile would otherwise stamp 0 (FAT) on
            # Windows and 3 (Unix) on Linux, changing the bytes for free.
            info.create_system = UNIX_CREATE_SYSTEM
            info.external_attr = FILE_MODE << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, source.read_bytes())


def human_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def verify_ruler_output() -> None:
    """Fail loudly if ruler did not produce something we expect to ship.

    Ruler's skills support is flagged experimental, so its output layout can
    move. Without this check that surfaces as a silently thin archive.
    """
    missing = [
        (tool, entry)
        for tool, _, paths in BUNDLES
        for entry in paths
        if not (ROOT / entry).exists()
    ]
    if missing:
        for tool, entry in missing:
            print(f"    MISSING ({tool}): {entry}", file=sys.stderr)
        sys.exit("Expected ruler output is missing. Run 'pnpm run ruler:apply' first.")


def clear_dist() -> None:
    if DIST.exists():
        for stale in sorted(DIST.rglob("*"), reverse=True):
            stale.unlink() if stale.is_file() else stale.rmdir()
    DIST.mkdir(exist_ok=True)


def render_notes(version: str, assets: list[dict]) -> str:
    asset_rows = "\n".join(
        f"| `{a['name']}` | {a['label']} | {a['size']} | `{a['sha256']}` |" for a in assets
    )
    content_rows = "\n".join(
        "| `{name}` | {paths} |".format(
            name=a["name"], paths=", ".join(f"`{p}`" for p in a["paths"])
        )
        for a in assets
    )
    return f"""\
**QRSPI** is a staged workflow for non-trivial coding tasks: eight user-invoked phases,
each writing one artifact that the next phase reads.

Each archive below holds the files for one AI coding tool, with paths relative to your
repository root. Download the one you want, verify it, and unzip it in place:

```bash
unzip -o qrspi-claude-{version}.zip
```

## Assets

| File | Tool | Size | SHA256 |
|---|---|---|---|
{asset_rows}

`SHA256SUMS.txt` covers every archive, and each one also ships a companion `.sha256`.
To verify:

```bash
sha256sum -c SHA256SUMS.txt
```

## What is in each bundle

| Bundle | Contents |
|---|---|
{content_rows}

Two things that look like packaging bugs but are not:

- **Cursor, Copilot, Codex and Gemini all share the root `AGENTS.md`.** Ruler does not
  write `.cursor/rules/` or `.github/copilot-instructions.md`.
- **The Copilot bundle contains `.claude/skills/`.** That is where Copilot reads skills
  from; ruler maps its `claude` skills target to Claude Code, Copilot and KiloCode alike.

Every file is generated from `.ruler/` by [ruler](https://ai.intellectronica.net/ruler).
To regenerate them yourself, clone the repo and run `pnpm install && pnpm run ruler:apply`.
"""


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"usage: {Path(sys.argv[0]).name} <version>")
    version = sys.argv[1]

    print("==> Verifying ruler output")
    verify_ruler_output()
    clear_dist()

    assets = []
    checksums = []
    for tool, label, paths in BUNDLES:
        name = f"qrspi-{tool}-{version}.zip"
        target = DIST / name
        files = collect(paths)
        build_zip(target, files)

        payload = target.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        # Two spaces between hash and name: the format `sha256sum -c` expects.
        line = f"{digest}  {name}"
        write_text(DIST / f"{name}.sha256", line + "\n")
        checksums.append(line)

        print(f"==> {name}: {len(files)} files, {human_size(len(payload))}")
        assets.append(
            {
                "name": name,
                "label": label,
                "paths": paths,
                "size": human_size(len(payload)),
                "sha256": digest,
            }
        )

    write_text(DIST / "SHA256SUMS.txt", "\n".join(checksums) + "\n")
    write_text(DIST / "RELEASE_NOTES.md", render_notes(version, assets))

    print("\n==> Done. dist/ contains:")
    for item in sorted(DIST.iterdir()):
        print(f"    {item.name}")


if __name__ == "__main__":
    main()
