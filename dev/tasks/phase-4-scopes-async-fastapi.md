# DI 2.0 — Phase 4: Scopes, async resolution, FastAPI glue

**Status:** done. Design → `dev/plans/di2-phase-4.md`. Staged under CHANGELOG
`[Unreleased]`; ship with the next `rc`. Closes the DI 2.0 roadmap.

Legend: `[x]` done · `[ ]` todo · `[~]` in progress

## Work
- [x] **`Scope.SCOPED` + `container.scope()`.** `_Scope` (per-scope instance cache
      + finalizers + lock) keyed off a `contextvars.ContextVar`;
      `_cached_instance`/`_build`/`_resolve_scoped` cache scoped instances and
      record scoped `@Resource` finalizers in the scope; `_require_scope` raises
      `ScopeError` with no active scope. `_ScopeHandle` is a sync+async context
      manager tearing the scope down (LIFO) on exit. Teardown refactored into
      shared `_teardown_sync`/`_teardown_async(finalizers, drop)`. `register()`
      and `register_provider()` accept singleton **or** scoped resources;
      `ResourceOptions.scope` carries it for the provider form.
- [x] **Full async resolution (`aget`).** `_aresolve`/`_abuild`/
      `_aresolve_singleton`/`_aresolve_scoped`/`_aconstruct`/`_aresolve_dependencies`/
      `_aresolve_dependency`/`_aautowire` mirror the sync path, awaiting an
      async-generator provider anywhere in the graph; the unresolved-dependency
      tail is shared with the sync path (`_unresolved_dependency`).
- [x] **FastAPI `Injected[T]`** (`di/integrations/fastapi.py`): `Injected[T]` →
      `Annotated[T, Depends(resolver)]`, `Injected(T, container=...)` → `Depends`;
      resolver runs `async with container.scope(): yield await container.aget(T)`.
      `fastapi` imported lazily; absent → `FrameworkIntegrationError`. mypy override
      keeps mypy from following fastapi into `anyio` under the 3.9 target.
- [x] `ScopeError`/`FrameworkIntegrationError`; exported `Injected` from `inito`.
- [x] Tests: `tests/di/test_scopes.py` (9), `tests/di/test_async_resolution.py`
      (15), `tests/di/test_fastapi_injected.py` (4, duck-typed fake `fastapi`).
- [x] Docs: DI page (Scopes → `SCOPED`, Async resolution, FastAPI sections +
      pieces/error rows), README, `docs/index.md`, `reference/dependency-injection.md`.
      CHANGELOG `[Unreleased]`.
- [x] Gate green (ruff/format/mypy strict/pytest **100%** coverage/docs -W);
      DI suite passes on Python 3.9.

## Out of scope (later/optional)
- Eager `init_resources()`, positional Factory args, non-FastAPI framework
  helpers, a request-shared scope across multiple `Injected` params (each opens
  its own scope in v1).

## After this
DI 2.0 roadmap complete → promote `1.0.0` (drop the `-rc` suffix) after a soak.
