---
name: qrspi-1-question
description: QRSPI phase 1 of 8 — decompose a task into neutral research questions. Run only when the user explicitly asks for the QRSPI question phase or invokes this skill. Takes a ticket file, issue URL, or task description.
---

# Question — Decompose the Task

Transform a task description into 3-7 specific, neutral research questions. These questions drive the next phase (Research) which runs in a **separate context with no knowledge of what is being built**.

This phase is reasoning-heavy. Use your most capable model; if your tool lets you switch models per task, switch up before continuing.

## Input

The user provides a task description, ticket file path, or issue reference — either with the invocation of this skill or in the surrounding conversation.

## Process

1. **Read any provided files fully** before doing anything else.

2. **Light codebase exploration**: Delegate this to the **codebase-locator** subagent if your tool supports subagents (Claude Code, Cursor, Codex, and Copilot receive them from this repo). If it doesn't, do the same work inline in this context, following the same constraint: describe what exists, and do not suggest improvements or propose solutions. You need to know what exists to write good questions.

3. **Decompose into 3-7 research questions**:
   - Each question should cause a researcher to explore a different relevant area of the codebase
   - Questions must be **neutral** — they ask what exists and how it works, never how to build something
   - Prefer "trace the flow" questions that reveal architecture over yes/no questions

   Good: "How does the middleware chain handle request authentication, and where are auth policies defined?"
   Bad: "What's the best way to add a new authenticated endpoint?"

   Good: "What patterns exist for database migrations, and how are they tested?"
   Bad: "How should we add a new migration for the users table?"

4. **Determine the artifact directory**:
   - With ticket number: `thoughts/qrspi/PROJ-1234-brief-description/` (use the project's ticket prefix)
   - Without ticket: `thoughts/qrspi/YYYY-MM-DD-brief-description/`

   Take today's date from your environment context. If it isn't available there, run `git log -1 --format=%cd --date=short` and use that. **Never guess the date.**

5. **Present the questions for approval before writing anything.**

   **Put this to the user and wait.** Use a structured multiple-choice question tool if your environment has one — `AskUserQuestion` in Claude Code, or the equivalent interactive prompt in your tool. If it has none, present the options as a numbered list and **stop**: end your turn and wait for the user's reply. Do not proceed on an assumed answer. The blocking is the point, not the tool.

   Ask one question per proposed research question that you are genuinely unsure about, or a single question asking whether the set is right, with options to accept, adjust scope, or redirect to different areas of the codebase. Incorporate the answers.

6. **Create the artifact directory** and write both files into it. Writing a file creates parent directories for you, so no shell command is needed.

7. **Write `task.md`** — a clean 2-3 sentence description of what's being built and why. This file persists the task context for later phases so the user doesn't have to re-explain it.

8. **Write `questions.md`**:

   ```markdown
   # Research Questions

   ## Context
   [2-3 sentences describing which areas of the codebase to focus on.
   Do NOT mention what is being built or why.]

   ## Questions
   1. [Neutral, fact-seeking question]
   2. [Neutral, fact-seeking question]
   ...
   ```

9. **Check the artifact policy.** QRSPI artifacts are working documents, not deliverables — `thoughts/` should be untracked. If the repo has no ignore rule covering it, tell the user (don't edit `.gitignore` yourself). Later phases rely on this: implementation commits stage source files only.

## Output

- Directory created: `thoughts/qrspi/<id>/`
- Files written: `thoughts/qrspi/<id>/task.md` and `thoughts/qrspi/<id>/questions.md`
- Tell the user: "Next: invoke the `qrspi-2-research` skill with `thoughts/qrspi/<id>/` (in most tools, `/qrspi-2-research thoughts/qrspi/<id>/`)."

## Rules

- `questions.md` must NOT contain the task description, goals, or desired behavior
- `task.md` is a brief, honest description of the goal — it will be read by later phases but NOT by Research
- The researcher who reads these questions should have no idea what feature is being built
- Each question should target a different area or concern
- Approval comes before the write, not after it
- If the task is too simple for 3 questions, tell the user — QRSPI is for complex tasks
