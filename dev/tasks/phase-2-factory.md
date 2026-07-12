# DI 2.0 — Phase 2: `Factory[T]` (call-time arguments)

**Status:** done. Design → `dev/plans/di2-phase-2.md`. Staged under CHANGELOG
`[Unreleased]`; ship with the next `rc`.

Legend: `[x]` done · `[ ]` todo · `[~]` in progress

## Goal
Inject a `Factory[T]` and call it to build a **fresh** `T` per call: registered-
typed constructor parameters are autowired, call-time keyword arguments supply
(and override) the rest, and anything left falls to the target's own default.

**Decisions (this session):** target need **not** be registered (prototype
factory); **call-time kwargs win**; keyword-only for v1.

## Work
- [x] `src/inito/di/factory.py` — public `Factory(Generic[T])` marker/type
      (`__call__(**kwargs) -> T`) and, in `container.py`, the private
      `_BoundFactory(Factory[Any])` the container injects.
- [x] `di/dependency_resolver.py` — `factory_target(hint) -> type | None`
      (`get_origin is Factory`) + `Dependency.factory_target` computed in
      `__post_init__` (reflect-once, alongside `registrable`/`qualifier`).
- [x] `di/container.py` — `_factory_plans` cache; extracted
      `_autowire(dep, path) -> instance | _MISSING` shared by
      `_resolve_dependency` and the factory; `_factory_plan`/`_make_factory`;
      `_resolve_dependency` refactored onto `_autowire`. Plan built once, eagerly,
      when the factory is injected (fail-fast on an unannotated target param).
- [x] Export `Factory` from `inito` and `inito.di`.
- [x] `tests/di/test_factory.py` (dep-free, 9): autowire + call-time arg;
      call-time kwarg overrides autowiring; fresh instance each call; call-time-
      only param required at the call; unregistered target (prototype); nested
      `Factory[...]`; `Factory` param breaks a would-be cycle; unannotated target
      param raises `DependencyRegistrationError` when the factory is injected;
      qualifier honored on a target dependency.
- [x] Docs: DI page "Factory (call-time arguments)" section + pieces table row;
      README DI section + concepts table + TOC; `reference/dependency-injection.md`
      (`autoclass:: inito.Factory`); `docs/index.md` DI paragraph.
- [x] Gate green (ruff/format/mypy strict/pytest 96.84%); `mypy` + pyright infer
      `make(...) -> T` with no plugin; factory tests pass on 3.9 & 3.10.

## Out of scope (this pass)
- Positional call-time arguments (keyword-only for v1).
- Static checking of the call-time kwargs themselves (return type `T` is checked;
  kwargs are `Any`).
