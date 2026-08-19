---
name: qrspi-5-plan
description: QRSPI phase 5 of 8 — expand the structure outline into a tactical implementation plan, the agent's working document. Run only when the user explicitly asks for the QRSPI plan phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
---

# Plan — Tactical Implementation Details

Expand the structure outline into a detailed, actionable implementation plan. This is the **agent's working document** — it should contain everything needed to implement without further context. The human reviews the design and structure; this document is for spot-checking.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding. If none exist, tell the user to run the QRSPI question phase first.

Read `<artifact-dir>/structure.md`, `<artifact-dir>/design.md`, `<artifact-dir>/research.md`, and `<artifact-dir>/task.md`.

## Process

1. **Read all four artifacts fully.** `task.md` is the shortest but anchors the Overview — the plan should open with the actual goal, not a paraphrase of the design.

2. **For each phase in `structure.md`**, expand into full implementation detail:
   - Exact file paths and what changes in each
   - Code snippets for non-trivial changes (new functions, type definitions, migrations)
   - Specific automated verification commands
   - Manual verification steps

3. **Write `plan.md`** to the artifact directory:

   ```markdown
   # Implementation Plan

   ## Overview
   [1-2 sentences from the design's desired end state]

   ## Phase 1: [Name from structure.md]

   ### Changes

   #### 1. [File or component group]
   **File**: `path/to/file.ext`
   **Action**: [create / modify / delete]

   ```language
   // Key code to add or modify
   ```

   #### 2. [Next file]
   ...

   ### Verification
   #### Automated
   - [ ] [project test/lint command] passes
   - [ ] [specific command for this phase]

   #### Manual
   - [ ] [what to check and expected behavior]

   ---

   ## Phase 2: [Name]
   ...
   ```

4. **Ensure completeness**:
   - Every file mentioned in `structure.md` must appear in the plan
   - No unresolved questions — if you find one, stop and ask the user
   - Verification steps must be concrete commands, not vague descriptions

5. **Present a brief summary** of the plan to the user. Note any places where you deviated from the structure outline and why.

## Output

- File written: `thoughts/qrspi/<id>/plan.md`
- Tell the user: "Next: **start a fresh context** — `/clear` in Claude Code, a new chat or session in other tools — then invoke the `qrspi-6-worktree` skill with `thoughts/qrspi/<id>/` to set up an isolated worktree, or `qrspi-7-implement` to implement in the current tree (in most tools, `/qrspi-6-worktree thoughts/qrspi/<id>/`). The artifacts are the handoff: that phase reads what it needs from disk, so carrying this session forward only costs context."

## Rules

- The plan must be self-contained. An agent reading only `plan.md` should be able to implement the feature.
- Follow the phase order from `structure.md`. Do not reorganize.
- Include code snippets for anything non-obvious. Skip boilerplate.
- Checkboxes (`- [ ]`) are mandatory for all verification steps — they track progress during implementation.
- No open questions in the final plan. Resolve or ask before writing.
- Use the verification commands `structure.md` already resolved. If that section is missing, fall back to the repo's agent instructions file (`CLAUDE.md`, `AGENTS.md`, or equivalent), Makefile, or package.json — never invent a command.
- Aim for a plan that's proportional to the work — roughly 1 line of plan per 1-2 lines of code expected.
- Only include changes described in `design.md` and `structure.md`. Do not add refactoring, cleanup, or improvements to adjacent code — even if it's obviously messy.
- If the plan includes schema migrations, include updating any test assertions that reference the current schema version.
- If the plan includes codegen steps, note what to do if codegen fails or is unavailable (e.g., manually adding fields to generated files as a fallback).

## When to Go Back

If expanding the structure reveals that a phase can't be implemented as outlined — missing information, incorrect assumptions, or a structural issue — tell the user and suggest re-running the `qrspi-4-structure` or `qrspi-3-design` skill rather than writing a plan you know is flawed.
