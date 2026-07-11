---
name: resume
description: Restore project context at the start of a session or after a break. Reads dev/README.md, the active phase's task file, and recent decisions so work can continue without re-scanning the codebase. Use when the user says "resume", "where were we", "continue", or starts a fresh session on inito.
---

# resume

Restore "where were we" from the durable `dev/` tracking — one small read, not a
codebase scan.

## Steps
1. Read `dev/README.md` → current version, active phase, status, and links.
2. Read the active phase's checklist under `dev/tasks/` (linked from README) →
   find the first unchecked `[ ]` / in-progress `[~]` item.
3. Skim the top of `dev/decisions.md` for any constraint relevant to the next step.
4. If mid-phase, read the phase design in `dev/plans/di2-phase-N.md`.
5. Report: current version, active phase, the next actionable task, and any
   blocking decision. Do **not** read `dev/history.md` (archive) unless a
   specific past detail is needed.

## Output
A 3–5 line status: released version · active phase · next task · anything pending
(e.g. an unpushed commit or an open release decision).
