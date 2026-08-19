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

[`.gitattributes`](.gitattributes) forces LF in the working tree on every platform. The prompt files
are shipped verbatim inside the release archives, so a CRLF checkout would hand users different bytes
than a CI build produces. Do not override this locally.

## Releases

[`.github/workflows/release.yml`](.github/workflows/release.yml) runs on every push to `main`. It
regenerates the tool files, packages them, and publishes a release tagged `v<version>` from
`package.json`. If that tag already exists the run is a no-op — **bump the version in
`package.json` to cut a release**.

The release notes open with a **What's Changed** section listing the PRs merged since the previous
release. CI asks GitHub to generate it (`gh api .../releases/generate-notes`, anchored on the last
published release, since the new tag does not exist until the release is created) and passes the
result to the build script as `--changelog`. Because it comes from GitHub, PRs are listed however
they were merged — squash, rebase or merge commit — so **the PR title is what readers see**. If the
API call fails the release still ships, with a warning and without the section.

To reproduce the archives locally:

```bash
pnpm run ruler:apply && python3 scripts/build_release_bundles.py 1.0.0
```

There is no release to compare a local build against, so it omits `--changelog` and renders the
notes without the **What's Changed** section; everything else is identical to what CI publishes.

Archives are deterministic (sorted entries, fixed timestamps and modes), so rebuilding the same
content always produces byte-identical archives — the changelog only affects `RELEASE_NOTES.md`.
Output lands in `dist/`, which is gitignored.

## Pull requests

- Keep the change scoped to `.ruler/` plus docs; do not commit generated files or `dist/`.
- Say which tool(s) you tested the change in.
- The methodology comes from [matanshavit/qrspi](https://github.com/matanshavit/qrspi) under the MIT
  license. Changes that alter the phases themselves are welcome, but note the divergence in the PR
  so it stays visible.

By contributing you agree that your work is licensed under the MIT license in
[`LICENSE`](LICENSE).
