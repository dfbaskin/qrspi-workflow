---
name: qrspi-4-structure
description: QRSPI phase 4 of 8 — structure outline breaking the design into vertical slices with test checkpoints. Run only when the user explicitly asks for the QRSPI structure phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
---

# Structure — How Do We Get There?

Create a ~2-page structure outline that breaks the design into **vertical slices** — each independently testable. Show the signatures, types, and phase boundaries — not the full implementation.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding. If none exist, tell the user to run the QRSPI question phase first.

Read `<artifact-dir>/design.md` and `<artifact-dir>/research.md`.

## Process

1. **Read both artifacts fully.**

2. **Find the project's real verification commands** before writing any checkpoint. Check the repo's agent instructions file (`CLAUDE.md`, `AGENTS.md`, or equivalent), then the build manifest (`Makefile`, `package.json` scripts, `pyproject.toml`, `Cargo.toml`, `*.csproj`, or equivalent), then CI config. You are about to author the checkpoints every later phase verifies against — they must be commands that actually exist in this project. If you can't find them, ask the user rather than inventing a plausible-looking `npm test`.

3. **Break the work into vertical slices.** Each slice delivers end-to-end functionality:
   - Crosses all necessary layers (database, service, API, UI) for that slice
   - Can be tested independently after implementation
   - Has a clear verification checkpoint

   **Vertical** (correct):
   > Phase 1: Add the "reticulate" endpoint — migration, store method, API handler, basic UI button. Test: endpoint returns 200, button triggers call.

   **Horizontal** (wrong):
   > Phase 1: All database migrations. Phase 2: All service methods. Phase 3: All API endpoints. Phase 4: All UI changes.

4. **Define the phase order.** Earlier phases should establish foundations that later phases build on. If Phase 3 fails, Phases 1-2 should still be independently valuable.

5. **For each phase, list**:
   - What it accomplishes (1-2 sentences)
   - Files affected
   - Key type signatures or interface changes
   - How to verify it works (the real command from step 2 + what to check manually)

6. **Write `structure.md`** to the artifact directory:

   ```markdown
   # Structure Outline

   ## Approach
   [1-2 sentences: the implementation strategy from design.md, condensed]

   ## Verification Commands
   [The project's actual test/lint/build commands, as found in step 2, with their source]

   ## Phase 1: [Name]
   [What this phase delivers end-to-end]

   **Files**: `path/to/file.ext`, `path/to/other.ext`
   **Key changes**:
   - `functionName(param: Type): ReturnType` — new/modified
   - `NewType { field: Type }` — new type

   **Verify**: [actual command] passes; [manual check description]

   ---

   ## Phase 2: [Name]
   ...

   ## Testing Checkpoints
   [Summary of what should be true after each phase, useful for resuming if context resets]
   ```

7. **Present the outline and ask for adjustments.**

   **Put this to the user and wait.** Use a structured multiple-choice question tool if your environment has one — `AskUserQuestion` in Claude Code, or the equivalent interactive prompt in your tool. If it has none, present the options as a numbered list and **stop**: end your turn and wait for the user's reply. Do not proceed on an assumed answer. The blocking is the point, not the tool.

   The common adjustments are a fixed set, so offer them directly: approve as written, reorder phases, split a phase that's too large, insert a testing phase between sensitive phases, or expand detail on a specific phase. Iterate until approved.

## Output

- File written: `thoughts/qrspi/<id>/structure.md`
- Tell the user: "Next: **start a fresh context** — `/clear` in Claude Code, a new chat or session in other tools — then invoke the `qrspi-5-plan` skill with `thoughts/qrspi/<id>/` (in most tools, `/qrspi-5-plan thoughts/qrspi/<id>/`). The artifacts are the handoff: that phase reads what it needs from disk, so carrying this session forward only costs context."

## Rules

- ~2 pages max. If it's longer, you're writing the plan, not the outline.
- Vertical slices, not horizontal layers. Every phase must cross all relevant layers.
- Signatures and types, not full implementation. Show WHAT changes, not HOW.
- Each phase must have a verification checkpoint built on a command that exists in this project.
- If the design calls for something that can't be sliced vertically, note it explicitly.

## When to Go Back

If you discover the design missed a critical constraint or made a decision based on incorrect assumptions about the codebase, tell the user and suggest re-running the `qrspi-3-design` skill rather than working around a flawed design.
