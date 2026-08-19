---
name: qrspi-7-implement
description: QRSPI phase 7 of 8 — execute the plan phase by phase with verification checkpoints and one commit per phase. Run only when the user explicitly asks for the QRSPI implement phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
disable-model-invocation: true
---

# Implement — Execute the Plan

Implement the plan one phase at a time, verifying each phase before proceeding. Update the plan's checkboxes as you go — they are your progress tracker and context-recovery mechanism.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding.

Read `<artifact-dir>/plan.md`. That is your primary working document.

## Process

1. **Read `plan.md` fully.** Check for existing checkmarks (`- [x]`) — if some phases are already complete, pick up from the first unchecked item.

2. **Branch preflight, before touching any code.** Determine the current branch and the repo's default branch. If you are on the default branch, stop and ask the user whether to create a feature branch or proceed anyway — this phase commits after every slice, and those commits should not land on the default branch by accident. Derive the proposed branch name from the artifact directory name, the same way the `qrspi-6-worktree` skill does (e.g. `ENG-1234-description` or `2026-03-29-new-feature`), so both routes produce the same name for a given task; propose it and let the user override. If the `qrspi-6-worktree` skill was run, you are already on the right branch and this check passes silently.

3. **Read all files referenced in the current phase** before making changes. Understand the code you're modifying.

4. **Implement one phase at a time:**
   - Make the changes described in the plan
   - Follow the plan's intent, but adapt if the codebase has diverged from what the plan expected
   - If you hit a mismatch, stop and present it:
     ```
     Issue in Phase [N]:
     Expected: [what the plan says]
     Found: [actual situation]
     Impact: [what this means for the plan]

     How should I proceed?
     ```

5. **After completing a phase, run verification:**
   - Execute the automated verification commands from the plan
   - If a command doesn't exist or won't launch, re-derive the right one from the repo's agent instructions file (`CLAUDE.md`, `AGENTS.md`, or equivalent), the build manifest, or CI config — then say which command you substituted and why. Never silently skip a check or mark it passed without running it.
   - Fix any failures before proceeding
   - Check off automated items in `plan.md`: `- [ ]` becomes `- [x]`

6. **Commit the phase** after automated verification passes. Each phase should be a separate commit so it can be independently reverted if later phases break something. Use a descriptive message like `"Phase N: [phase name from plan]"`.

   **Stage the source files for this phase by name.** Do not blanket-stage — QRSPI artifacts under `thoughts/` are untracked working documents, and you are editing `plan.md` checkboxes as part of this same phase. They do not belong in the commit.

7. **Pause for manual verification** (unless told to continue through multiple phases):
   ```
   Phase [N] complete — ready for manual verification.

   Automated checks passed:
   - [x] [list what passed]

   Please verify manually:
   - [ ] [manual items from the plan]

   Let me know when done, and I'll proceed to Phase [N+1].
   ```

8. **Repeat** for each phase until the plan is complete.

## Resuming After Context Reset

If you're starting fresh in a new context window:
- Read `plan.md` — checked boxes show what's done
- Trust completed work unless something seems off
- Pick up from the first unchecked item

## Output

- Code changes implemented according to the plan
- `plan.md` updated with checked verification items
- One commit per completed phase
- Tell the user: "Next: **start a fresh context** — `/clear` in Claude Code, a new chat or session in other tools — then invoke the `qrspi-8-pr` skill with `thoughts/qrspi/<id>/` (in most tools, `/qrspi-8-pr thoughts/qrspi/<id>/`). The artifacts are the handoff: that phase reads what it needs from disk, so carrying this session forward only costs context."

## Rules

- One phase at a time. Do not skip ahead.
- Read before you write. Understand existing code before changing it.
- Update checkboxes as you go — they are the source of truth for progress.
- Do not check off manual verification items until the user confirms.
- Stage explicitly. Never blanket-stage the working tree.
- If the plan has errors, stop and ask. Do not silently deviate.
- Only make changes described in the plan. Do not refactor, clean up, or "improve" code you encounter along the way — even if it's messy. If you see something worth fixing, note it for the user after the phase is done.
- Use sub-agents sparingly — only for targeted debugging or exploring unfamiliar code.
- Commit after each phase passes automated verification — one commit per phase.

## When to Go Back

If a phase reveals the plan is fundamentally wrong — not a small mismatch but a structural issue like a missing dependency, wrong API, or incorrect assumption about the codebase — tell the user. For small mismatches, adapt and continue. For fundamental issues, suggest re-running the `qrspi-5-plan` or even the `qrspi-3-design` skill with the new information rather than building on a broken foundation.
