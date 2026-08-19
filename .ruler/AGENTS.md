# QRSPI Workflow

This repo distributes **QRSPI**, a staged workflow for non-trivial coding tasks. Each stage runs as a
user-invoked skill and writes one artifact; later stages read the earlier artifacts rather than
re-deriving context. The point is to separate *what exists* from *what we want* from *how we get
there*, and to put approval gates at the cheapest points to change direction.

## The phases

| Skill | Produces | Purpose |
|---|---|---|
| `qrspi-1-question` | `task.md`, `questions.md` | Decompose the task into 3-7 neutral research questions |
| `qrspi-2-research` | `research.md` | Answer them from the codebase — facts and `file:line` refs only |
| `qrspi-3-design` | `design.md` | Agree on the destination and the decisions behind it |
| `qrspi-4-structure` | `structure.md` | Break the design into vertical, independently testable slices |
| `qrspi-5-plan` | `plan.md` | Expand the slices into a self-contained implementation plan |
| `qrspi-6-worktree` | a git worktree | *Optional* — isolate the work on its own branch |
| `qrspi-7-implement` | code, one commit per phase | Execute the plan, verifying at each checkpoint |
| `qrspi-8-pr` | a pull request | Open the PR with the reasoning inlined |

Run them in order. Phase 2 deliberately runs blind to the task description so its findings stay
objective — that isolation is the reason the phases are separate.

## Artifacts

Everything lives in one directory per task: `thoughts/qrspi/<id>/`, where `<id>` is either
`PROJ-1234-brief-description` or `YYYY-MM-DD-brief-description`. Most phases accept that directory
as an argument and fall back to the most recently modified one.

These are working documents, not deliverables — **`thoughts/` should be untracked**. Implementation
commits stage source files by name, never the whole tree.

## Invocation

These are explicit, user-invoked phases. Do not start one on your own initiative, and do not run
ahead to the next phase after finishing one — report the artifact and stop.

Each phase runs in its own fresh context. Start a new one (`/clear` in Claude Code, a new chat or
session in other tools) before invoking the next phase, so it reads its inputs from the artifacts
rather than inheriting the previous session. Writing the artifact is only half of the compaction;
discarding the context that produced it is the other half. Phase 2 depends on this most — it must
not know what is being built.
