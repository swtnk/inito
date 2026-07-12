# DI 2.0 — Phase 4: Scopes, async resolution, framework glue

## Context

The last gaps vs. `dependency-injector`: a **request/task-scoped** lifetime, a
fully **async** resolution path (so an async `@Resource` can be a dependency, not
just a top-level `aget`), and first-class **framework wiring** (FastAPI). After
this, the roadmap's parity table is fully ticked and inito can be promoted to a
stable `1.0.0`.

## Scope

**In:**
1. **`Scope.SCOPED` + `container.scope()`.** A scope is a `contextvars`-based
   lifetime: within `with container.scope():` / `async with container.scope():`,
   a `SCOPED` service is built once and cached in the scope; a `SCOPED`
   `@Resource` is torn down (LIFO) at scope exit. Resolving a `SCOPED` service
   with no active scope raises. Scopes nest (the innermost wins) and are
   task/thread-local via a `ContextVar`.
2. **Full async resolution (`await container.aget(cls)`).** An async twin of the
   resolve path (`_aresolve`/`_abuild`/`_aresolve_singleton`/`_aresolve_scoped`/
   `_aconstruct`) that awaits async-generator providers **anywhere in the graph**,
   not only at the top. Sync `get()` is unchanged (still raises helpfully on an
   async provider). Shared, side-effect-free helpers (cycle check, cache lookup,
   `_pick_implementation`, qualifier lookup, `_class_finalizer`) are reused.
3. **FastAPI `Injected[T]`.** `Injected[T]` -> `Annotated[T, Depends(resolver)]`
   where the resolver runs `await container.aget(T)` inside a per-request
   `container.scope()` (setup/teardown via a FastAPI `yield` dependency).
   **Zero-dependency:** `fastapi` is imported lazily, only when `Injected` is
   used (duck-typed optional path, like Pydantic); absent -> a clear error.

**Out (later/optional):** eager `init_resources()`, positional Factory args,
non-FastAPI framework helpers, scoped *sync-generator* providers with async
teardown mixing.

## Design

### `Scope.SCOPED` + `_Scope` (`di/container.py`)
- New `Scope.SCOPED`.
- `_current_scope: ContextVar[_Scope | None]`. `_Scope` holds `instances:
  dict[type, Any]`, `finalizers: list[_Finalizer]`, a `Lock`.
- `_cached_instance`: `SCOPED` -> the current scope's `instances` (or `_MISSING`).
- `_build`/`_abuild`: `SCOPED` -> `_resolve_scoped`/`_aresolve_scoped` — resolve
  deps, construct, cache in the scope, and record any resource finalizer **in the
  scope** (not the container). No active scope -> `UnresolvableDependencyError`.
- `register()`: a `@Resource` may be `SINGLETON` **or** `SCOPED` (not
  transient/thread-local). `ResourceOptions` gains `scope` for provider form;
  `register_provider(spec, scope=...)`.
- `container.scope()` returns a handle usable as both `with` and `async with`;
  on exit it resets the ContextVar and tears the scope's finalizers down
  (sync exit raises if an async finalizer is pending, like `shutdown_resources`).
- Refactor teardown into shared `_teardown_sync(finalizers, drop)` /
  `_teardown_async(finalizers, drop)`; container shutdown and scope exit both use
  them (`drop` removes the cached instance from the right place).

### Async resolution (`di/container.py`)
- `aget` -> `await self._aresolve(cls, ())`. `_aresolve` mirrors `_resolve`;
  `_abuild` branches on scope; `_aresolve_singleton`/`_aresolve_scoped` await
  `_aresolve_dependencies` then `_aconstruct`; `_aconstruct` awaits an
  async-generator provider's first yield, else delegates to sync `_construct`.
- `_aresolve_dependencies`/`_aresolve_dependency`/`_aautowire` mirror the sync
  trio; a `Factory[T]` still injects the sync `_BoundFactory`.

### FastAPI `Injected[T]` (`di/integrations/fastapi.py`, new)
- `Injected.__class_getitem__(item)` -> `Annotated[item, Depends(_provider)]`
  where `_provider` is an async FastAPI dependency: `async with
  container.scope(): yield await container.aget(item)`.
- Callable form `Injected(T, container=...)` -> `Depends(...)` for a default value.
- `fastapi` imported inside these functions only; missing -> `InitoError`
  subclass with an actionable message.
- Export `Injected` from `inito` (module import must not import fastapi).

### Errors & exports
- `ScopeError(InitoError)` — resolving a scoped service with no active scope;
  reuse `ResourceTeardownError` for scope teardown failures.
- Export `Injected` from `inito`; `Scope.SCOPED` already exported via `Scope`.

## Verification
Dep-free tests (async via `asyncio.run`): scoped instance is one-per-scope and
distinct across scopes; scoped resource torn down at scope exit (sync + async,
LIFO); scoped-with-no-scope raises; nested scopes; async `aget` builds a graph
whose dependency is an async-generator provider; async provider as a constructor
dep of an async-built class; `Injected[T]` resolves via a duck-typed fake
`Depends`/`fastapi`, opens/closes a scope per request, and errors clearly when
fastapi is absent. Full gate (ruff/format/mypy strict/pytest 100%/docs -W) and a
Python 3.9 run. Then cut `rc6` (or promote to `1.0.0`).
