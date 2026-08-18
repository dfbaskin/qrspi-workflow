# Contributing

Thanks for taking an interest. This repo packages the QRSPI workflow for five AI coding tools, so
almost every change is a change to a prompt in `.ruler/` — the rest of the tree is generated.

## Prerequisites

- Node.js — ruler requires `^20.19.0 || ^22.12.0 || >=23` (CI uses 22)
- pnpm — the version is pinned by `packageManager` in [`package.json`](package.json)
- Python 3 — only needed to build release archives locally

```bash
pnpm install
```

## Repo layout

`.ruler/` is the only hand-authored source: one `AGENTS.md`, eight skills, four subagents.

```
.ruler/
  AGENTS.md              root instruction file, copied to CLAUDE.md / AGENTS.md
  ruler.toml             which tools to target; subagent propagation
  skills/qrspi-N-*/SKILL.md
  agents/*.md            subagents (codebase-locator, -analyzer, -pattern-finder, web-search-researcher)
scripts/build_release_bundles.py
.github/workflows/release.yml
```

Everything ruler generates — `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.cursor/`, `.codex/`,
`.gemini/`, `.github/agents/` — is gitignored inside the managed block in
[`.gitignore`](.gitignore). Never edit those files directly; your change will be overwritten by the
next `ruler apply` and will not reach any release archive.

## Generating the tool files

```bash
pnpm run ruler:apply
```

`pnpm run ruler:check` does a dry run with verbose output, and `pnpm run ruler:revert` removes the
generated files. Run `ruler:apply` after editing anything under `.ruler/`, then exercise the phase
in the tool you care about before opening a PR.

## Editing skills and subagents

Each skill is a directory under `.ruler/skills/` holding a single `SKILL.md` with YAML frontmatter:

```yaml
---
name: qrspi-1-question
description: QRSPI phase 1 of 8 — ... Run only when the user explicitly asks for ...
---
```

Conventions worth keeping:

- The `name` must match the directory name and the phase number.
- The `description` says what the phase produces and states that it is user-invoked. These phases
  are explicit gates; a description that invites auto-invocation defeats the design.
- Skills must not assume Claude Code. Where a phase wants a subagent, say what to do when the tool
  has none — the existing skills all describe the inline fallback.
- Subagents in `.ruler/agents/` carry `name`, `description`, `tools` and `model` frontmatter.
  Keep the research-phase agents strictly descriptive; their value depends on being opinion-free.

If you add or remove a phase, update the table in [`README.md`](README.md), the table in
`.ruler/AGENTS.md`, and any cross-references in neighbouring skills.

## Line endings

[`.gitattributes`](.gitattributes) forces LF in the working tree on every platform. Release archives
are hashed, and a CRLF checkout would silently change every SHA256 relative to CI. Do not override
this locally.

## Releases

[`.github/workflows/release.yml`](.github/workflows/release.yml) runs on every push to `main`. It
regenerates the tool files, packages them, and publishes a release tagged `v<version>` from
`package.json`. If that tag already exists the run is a no-op — **bump the version in
`package.json` to cut a release**.

To reproduce the archives locally:

```bash
pnpm run ruler:apply && python3 scripts/build_release_bundles.py 1.0.0
```

Archives are deterministic (sorted entries, fixed timestamps and modes), so the same content always
produces the same SHA256. Output lands in `dist/`, which is gitignored.

## Pull requests

- Keep the change scoped to `.ruler/` plus docs; do not commit generated files or `dist/`.
- Say which tool(s) you tested the change in.
- The methodology comes from [matanshavit/qrspi](https://github.com/matanshavit/qrspi) under the MIT
  license. Changes that alter the phases themselves are welcome, but note the divergence in the PR
  so it stays visible.

By contributing you agree that your work is licensed under the MIT license in
[`LICENSE`](LICENSE).
