# inito — dev tracking (start here)

The durable, resumable source of truth for ongoing work. A new session should
read **this file first** (or run the `resume` skill) — it restores "where were
we" from one small read instead of scanning the codebase.

## Current status

- **Released:** `1.0.0-rc5` on PyPI (DI 2.0 `Factory[T]` + `@Resource` lifecycle).
  All Initial Features + `@Value` + DI v1/v2-so-far complete. CI green on Python
  3.9–3.14 + framework interop; test suite at **100% coverage**.
- **pyright gap closed:** `inito-stubgen` generates `.pyi` stubs giving pyright
  full visibility of every generated member (see
  [`tasks/pyright-stubgen.md`](tasks/pyright-stubgen.md)).
- **Active work:** **DI 2.0** — cover the cases `dependency-injector` solves, in
  inito's zero-dependency, annotation-native way. See [`roadmap.md`](roadmap.md).
- **Done:** **DI 2.0 complete** — Phase 1 (overrides · config · qualifiers ·
  thread-local), Phase 2 ([`Factory[T]`](tasks/phase-2-factory.md)), Phase 3
  ([`@Resource`](tasks/phase-3-resources.md)), Phase 4
  ([scopes · async `aget` · FastAPI `Injected`](tasks/phase-4-scopes-async-fastapi.md)).
- **Next:** promote to stable **`1.0.0`** (drop the `-rc` suffix) after an rc soak.
  Phases 2–4 are staged in CHANGELOG `[Unreleased]`, to ship as the next `rc`.

## Map

| File | Purpose |
|---|---|
| [`roadmap.md`](roadmap.md) | DI 2.0 phased plan + capability→annotation-native design table |
| [`tasks/`](tasks/) | Active per-phase checklists (only near-term work) |
| [`plans/`](plans/) | Durable copies of each phase's detailed design plan |
| [`decisions.md`](decisions.md) | Short ADR log — key design decisions and why |
| [`history.md`](history.md) | Archived Phases 0–22 (finished; reference only) |

## How work is tracked

1. Each DI 2.0 phase gets a design plan in `plans/di2-phase-N.md` and a checklist
   in `tasks/phase-N-*.md`.
2. Update the checklist and this file's **Current status** as work lands.
3. Record any non-obvious design decision in `decisions.md`.
4. Ship each phase as its own `1.0.0-rcN`/patch (see the `release` skill).

## Tooling (see `.claude/`)

- **Skills:** `resume`, `gate` (full check run), `di-feature` (add a DI capability
  the inito way), `release`.
- **Agents** (use deliberately, not by default): `explorer`, `convention-reviewer`,
  `test-author`, `doc-writer`, `di-designer`.
- **Rules:** [`.claude/rules/python.md`](../.claude/rules/python.md) — the coding
  standards every change must meet.
