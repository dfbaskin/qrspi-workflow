---
name: qrspi-8-pr
description: QRSPI phase 8 of 8 — create a pull request with context drawn from the design discussion and the actual diff. Run only when the user explicitly asks for the QRSPI PR phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
disable-model-invocation: true
---

# PR — Create the Pull Request

Create a pull request with a description grounded in the design document and the actual diff.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding.

Read `<artifact-dir>/design.md` for the "why" and `<artifact-dir>/plan.md` for the verification steps — its checkboxes are already written and belong in the PR body.

## Process

1. **Preflight.** Resolve each of these before writing anything:
   - **Base branch** — try `git symbolic-ref refs/remotes/origin/HEAD` first; it is frequently unset on fresh clones, so fall back to `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, then to `main`, then `master`. Report which one you used.
   - **Uncommitted changes** — if the tree is dirty, stop and ask. Do not commit on the user's behalf here; that's the `qrspi-7-implement` phase's job.
   - **Unpushed branch** — if the branch has no upstream, push it with `git push -u origin <branch>`.
   - **Existing PR** — check `gh pr view --json url`. If one exists for this branch, update it with `gh pr edit` instead of creating a second.
   - **Auth** — if `gh` isn't authenticated, say so and stop rather than failing mid-command.

2. **Gather the change:**
   - `git diff <base>...HEAD` — the full diff
   - `git log <base>...HEAD --oneline` — commit history (one commit per implementation phase)

3. **Write the PR body to a file**, then pass it to `gh`. Write the body to a temporary path with your file-writing tool — do not build multi-line text with a shell heredoc, which is not portable across shells.

   ```markdown
   ## Summary
   [2-3 bullets: what this PR does and why, drawn from design.md]

   ## Design Decisions
   [Key decisions from design.md, stated inline with their reasoning.
   Write them out in full — QRSPI artifacts are untracked, so a reviewer
   cannot open the design document from this PR.]

   ## Changes
   [Brief description of what changed, organized by component if multi-component]

   ## How to Verify
   - [ ] [Automated verification command, from plan.md]
   - [ ] [Manual verification step, from plan.md]
   ```

4. **Create the PR:**

   ```
   gh pr create --base <base> --title "<concise title under 70 chars>" --body-file <path to body file>
   ```

5. **Clean up** the temporary body file and **report the PR URL** to the user.

## Output

- PR created (or existing PR updated) on GitHub
- URL reported to the user

## Rules

- Title under 70 chars. Use the body for details.
- The summary should explain WHY, not just WHAT. The diff shows what changed; the PR description should explain the reasoning.
- Inline the design reasoning. Do not link to `thoughts/qrspi/<id>/` paths — those files are untracked and reviewers cannot open them.
- Pull "How to Verify" from `plan.md` rather than inventing steps; those commands were already validated during implementation.
- Never assemble the body with a heredoc or inline shell quoting — write a file and use `--body-file`.
