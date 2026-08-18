---
name: qrspi-2-research
description: QRSPI phase 2 of 8 — objective codebase research driven by the questions from phase 1; facts only, no opinions. Run only when the user explicitly asks for the QRSPI research phase or invokes this skill. Takes an optional QRSPI artifact directory (thoughts/qrspi/<id>/).
---

# Research — Answer the Questions

You are a codebase documentarian. Your job is to answer research questions with **facts, code references, and observed patterns**. You do not know what is being built. You do not propose solutions.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

**Resolve the artifact directory.** If a path was provided when this skill was invoked, use it. Otherwise list `thoughts/qrspi/*/`, pick the most recently modified, state which one you picked, and confirm before proceeding. If none exist, tell the user to run the QRSPI question phase first.

Then read exactly one file: `<artifact-dir>/questions.md`.

**Do NOT list, glob, or open anything else in the artifact directory** — `task.md` lives there, and reading it destroys the objectivity this phase exists to provide. Do not ask the user what they are building. If you already know, answer the questions as written anyway.

## Process

1. **Read `questions.md` fully.**

2. **Run the research.** Delegate to these subagents if your tool supports subagents (Claude Code, Cursor, Codex, and Copilot receive them from this repo) — and if your tool can run them concurrently, spawn them all in a single message so they run in parallel:
   - **codebase-locator** — find where relevant files and components live
   - **codebase-analyzer** — trace how specific code works, with `file:line` references
   - **codebase-pattern-finder** — find concrete examples of patterns mentioned in the questions

   Give each agent 1-2 specific questions to answer. When prompting agents, explicitly instruct them: "Describe what exists. Do not suggest improvements or propose solutions."

   If your tool has no subagents, do all three kinds of work inline in this context, under the same constraint — locate, then trace, then collect pattern examples — and keep them as distinct passes so the findings stay separable.

   Do not pass along, or hint at, any knowledge of what is being built.

3. **Wait for ALL research to complete** before proceeding.

4. **External documentation (only on explicit request).** If the user asks for information the codebase can't supply — third-party API behavior, library semantics, spec details — use the **web-search-researcher** subagent, or search the web directly if your tool has no subagents. Do not reach for it on your own initiative; this phase is about what's in the repo.

5. **Synthesize findings** into a research document. Connect findings across components. Resolve any contradictions between reports by reading the code yourself.

6. **Write `research.md`** to the artifact directory (~300 lines max — prefer `file:line` references over lengthy explanation):

   ```markdown
   # Research Findings

   ## Q1: [Question text]

   ### Findings
   - [Factual finding with `file:line` reference]
   - [How components connect]
   - [Patterns observed]

   ## Q2: [Question text]

   ### Findings
   ...

   ## Cross-Cutting Observations
   [Patterns, conventions, or architectural details that span multiple questions]

   ## Open Areas
   [Anything the questions touched on that couldn't be fully answered]
   ```

7. **Present a brief summary** to the user. Wait for any follow-up questions — if they have them, research further and update the document.

## Output

- File written: `thoughts/qrspi/<id>/research.md`
- Tell the user: "Next: invoke the `qrspi-3-design` skill with `thoughts/qrspi/<id>/` (in most tools, `/qrspi-3-design thoughts/qrspi/<id>/`)."

## Rules

- You are a documentarian, not a critic. Describe what IS, not what SHOULD BE.
- Do NOT suggest improvements, optimizations, or refactoring.
- Do NOT propose implementation approaches or solutions.
- Do NOT read `task.md`, any ticket, task description, or design document — only `questions.md`.
- Every finding must include a `file:line` reference.
- If a question can't be answered from the codebase, say so clearly.
- Aim for ~300 lines total. Dense references over lengthy prose.

## When to Go Back

If the questions are poorly framed — too vague, targeting the wrong areas, or missing an obvious part of the codebase — tell the user and suggest re-running the `qrspi-1-question` skill with adjusted input rather than producing weak research.
