---
name: qrspi-3-design
description: QRSPI phase 3 of 8 — design discussion; align on where we are going before planning how. Run only when the user explicitly asks for the QRSPI design phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
---

# Design — Where Are We Going?

Create a ~200-line design document that captures the current state, desired end state, design decisions, and patterns to follow. This is the **lowest-cost point for direction changes** — get alignment here before investing in detailed planning.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding. If none exist, tell the user to run the QRSPI question phase first.

Read `<artifact-dir>/task.md`, `<artifact-dir>/questions.md`, and `<artifact-dir>/research.md`.

## Process

1. **Read all three artifacts fully.** `task.md` tells you what we're building. `research.md` tells you what exists. Understand both before proceeding.

2. **Targeted exploration**: If the research revealed areas that need deeper investigation for design decisions, delegate to the **codebase-pattern-finder** or **codebase-analyzer** subagents if your tool supports subagents (Claude Code, Cursor, Codex, and Copilot receive them from this repo). If it doesn't, examine those specific patterns or approaches inline in this context.

3. **Put the open decisions to the user and wait.** Before writing anything, you MUST present 3-5 design decisions that require human judgment.

   **Put this to the user and wait.** Use a structured multiple-choice question tool if your environment has one — `AskUserQuestion` in Claude Code, or the equivalent interactive prompt in your tool. If it has none, present the options as a numbered list and **stop**: end your turn and wait for the user's reply. Do not proceed on an assumed answer. The blocking is the point, not the tool.

   For each decision:
   - Frame it as the actual choice being made, not "what do you think about X"
   - Give 2-4 concrete options drawn from what the research found
   - State the trade-off in each option's description, citing the `file:line` where that pattern already lives
   - Lead with your recommendation and mark it `(Recommended)`

   Example of a well-formed option set:

   > **Q: Data model approach**
   > - *Reuse the EventStore envelope (Recommended)* — matches `stores/events.ts:44`; simpler, but locks rows to a single tenant
   > - *New table with a join* — mirrors `stores/audit.ts:112`; more flexible, adds a migration and a second query path

   Do NOT skip this step. Do NOT write the design document without user input. If a decision turns out to have only one viable option, say so and drop it rather than padding the question set.

4. **Write `design.md`** (~200 lines) to the artifact directory:

   ```markdown
   # Design Discussion

   ## Current State
   [What exists today, grounded in research findings with file:line refs]

   ## Desired End State
   [What we're building and how to verify it's correct]

   ## Patterns to Follow
   [Existing codebase patterns the implementation should match, with file:line refs.
   Flag any patterns the research found that should NOT be followed.]

   ## Design Decisions
   1. **[Decision name]**: [chosen option] — [why]
   2. **[Decision name]**: [chosen option] — [why]
   ...

   ## What We're NOT Doing
   [Explicit scope boundaries to prevent creep]

   ## Open Risks
   [Anything uncertain that might surface during implementation]
   ```

   Every decision recorded here must trace back to an answer from step 3. If you had to decide something the user wasn't asked about, mark it explicitly as an assumption under Open Risks.

5. **Present the design for review.** Summarize what changed from the answers you were given, then ask — blocking the same way as in step 3 — whether to approve as written, revise a specific section, or reopen a decision. Iterate until approved.

## Output

- File written: `thoughts/qrspi/<id>/design.md`
- Tell the user: "Next: **start a fresh context** — `/clear` in Claude Code, a new chat or session in other tools — then invoke the `qrspi-4-structure` skill with `thoughts/qrspi/<id>/` (in most tools, `/qrspi-4-structure thoughts/qrspi/<id>/`). The artifacts are the handoff: that phase reads what it needs from disk, so carrying this session forward only costs context."

## Rules

- ~200 lines max. This is a steering document, not a specification.
- Every pattern reference must cite `file:line` from the research.
- You MUST block for user answers before writing. No exceptions.
- "Patterns to Follow" is critical — call out both good and bad patterns found in the codebase.
- "What We're NOT Doing" prevents scope creep downstream.

## When to Go Back

If the research is missing critical information needed for design decisions — the questions missed an important area of the codebase — tell the user and suggest re-running the `qrspi-1-question` and `qrspi-2-research` skills to fill the gap before proceeding with an incomplete design.
