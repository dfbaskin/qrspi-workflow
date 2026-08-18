---
name: qrspi-6-worktree
description: QRSPI phase 6 of 8 — create an isolated git worktree for implementation. Optional; skip it to implement in the current tree. Run only when the user explicitly asks for the QRSPI worktree phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
disable-model-invocation: true
---

# Worktree — Isolate the Implementation

Create a git worktree so implementation happens on an isolated branch without affecting your main working tree.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding.

Confirm `<artifact-dir>/plan.md` exists. If it doesn't, stop and tell the user to run the `qrspi-5-plan` skill first.

## Process

1. **Determine identifiers:**
   - **Branch name** — derive from the artifact directory name (e.g. `ENG-1234-description` or `2026-03-29-new-feature`)
   - **Repo name** — the final path segment of `git rev-parse --show-toplevel`
   - **Worktree path** — a sibling of the repo, in a `wt` directory: `<parent-of-repo>/wt/<repo-name>/<branch-name>`. Resolve it to an absolute path; do not emit a `~`-prefixed path, which does not expand in every shell.
   - **Base branch** — the repo's default branch unless the user says otherwise

2. **Preflight.** Check all of these and report anything that fails instead of pushing through:
   - Does the branch already exist (`git rev-parse --verify <branch>`)? If so, offer to reuse it (`git worktree add <path> <branch>`, no `-b`) or pick a new name.
   - Is anything already at the worktree path? If so, stop — do not overwrite.
   - Are there uncommitted changes in the current tree? They stay behind; make sure the user knows.
   - Is the base branch current? Offer to fetch first.

3. **Confirm before creating anything:**

   ```
   Ready to create worktree:

   Worktree: <absolute worktree path>
   Branch:   <branch-name> (from <base-branch>)
   Plan:     <artifact-dir>/plan.md

   Proceed?
   ```

4. **Create the worktree** only after the user confirms:

   ```
   git worktree add <absolute worktree path> -b <branch-name> <base-branch>
   ```

5. **Copy the artifact directory** into the worktree at the same relative path. Worktrees do not share untracked files with the main tree, and QRSPI artifacts are untracked — without this step the implementation phase has no plan to read. Copy it with the file tools or a shell command appropriate to the current platform.

6. **Flag what else the worktree is missing.** A fresh worktree has no ignored files: no installed dependencies, no local `.env` or equivalent secrets, no build output. Report which of these the project needs so the user can set them up. Do not copy secrets on your own initiative.

   If the project uses [ruler](https://github.com/intellectronica/ruler) to distribute agent instructions, the generated per-tool files are gitignored and will be missing too — run `ruler apply` in the new worktree.

7. **Hand off.** Implementation runs in a separate context window from the worktree directory. Tell the user to open a new session with the worktree as its working directory, then invoke the `qrspi-7-implement` skill with `<artifact-dir>` (in most tools, `/qrspi-7-implement <artifact-dir>`).

## Output

- Git worktree created at the reported absolute path
- QRSPI artifacts copied into the worktree
- Missing local setup (dependencies, env files) reported
- Handoff instructions given

## Rules

- Always confirm before creating the worktree. Nothing is created before step 4.
- Never emit `~`-prefixed paths — resolve to absolute.
- Worktrees do not share untracked files with the main tree. Always copy the artifact directory after creating the worktree.
- Do not start implementation. That's a separate phase with a separate context window.

## When to Go Back

If `<artifact-dir>/plan.md` doesn't exist, tell the user to run the `qrspi-5-plan` skill first.
