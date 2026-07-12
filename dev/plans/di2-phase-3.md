# DI 2.0 — Phase 3: Resource lifecycle (`@Resource`)

## Context

A `@Singleton` is built once and lives for the container's life — but real
resources (DB pools, HTTP/redis/boto clients, sessions) must also be **closed**,
in the reverse of the order they were opened. `dependency-injector` solves this
with a `Resource` provider + `init_resources()`/`shutdown_resources()`. InitO's
annotation-native equivalent is `@Resource` plus a container that is a (sync and
async) context manager.

**Decision (this session):** support **both models** — a `@Resource` *class*
(torn down by its `close()`/`aclose()` method or the context-manager protocol)
**and** a `@Resource` *generator-provider function* (`yield resource` then
cleanup). Reflect-once and zero-dependency preserved.

## Scope

**In:**
- **Class form.** `@Resource` marks a `@Service`/`@Singleton` class. Teardown via
  a `close()` method (name configurable, `@Resource(close="aclose")`), or — if it
  has none — the `__enter__`/`__exit__` protocol (entered at build, exited at
  teardown). Sync construction. Sync teardown *or* async teardown (an `aclose`
  coroutine).
- **Function form.** `@Resource` on a **generator** function self-registers a
  provider keyed by the yielded type: `def pool(dsn: str) -> Iterator[Pool]:
  p = Pool(dsn); yield p; p.close()`. The function's parameters are autowired.
  Sync generators build via `get()`; **async** generators build via
  `await container.aget()`.
- **Container lifecycle.** LIFO `_resource_finalizers`; `shutdown_resources()`
  (sync; raises `ResourceTeardownError` if an async resource is present),
  `await ashutdown_resources()`; `with container:` / `async with container:`;
  `container.aget(cls)`. `reset()` drops finalizers (test helper). Teardown is
  best-effort: every resource is closed, errors aggregated into one
  `ResourceTeardownError`.

**Out (→ Phase 4):** `Scope.SCOPED` / `container.scope()`, full async dependency
resolution (`aget` resolves an async provider's *own* deps through the sync path,
so nesting an async provider as a constructor dep of a sync-built class is a
Phase 4 concern), FastAPI `Injected[T]`. Async **construction** beyond advancing
one async generator to its first yield stays out; async class resources need only
sync construction + async `aclose`, which is fully covered here.

## Design

### `di/resource.py` (new, pure detection — no container import)
- `RESOURCE_ATTRIBUTE = "__inito_resource__"` — class-form marker (a data marker,
  same pattern as `METADATA_ATTRIBUTE`).
- `ProviderKind(Enum)`: `SYNC_GENERATOR`, `ASYNC_GENERATOR`.
- `ResourceSpec(frozen)`: `close_method: str | None`, `is_context_manager: bool`,
  `is_async: bool` (class form).
- `ProviderSpec(frozen)`: `factory`, `provided_type`, `kind` (function form).
- `class_resource_spec(cls, close_name)`: close method → CLOSE (async iff
  coroutine); else `__exit__` → CM; else `__aexit__` → raise (async CM deferred);
  else raise. Computed **once** at decoration.
- `provider_spec(fn)`: `isgeneratorfunction`/`isasyncgenfunction` → kind;
  provided type from the `Iterator[X]`/`AsyncIterator[X]`/`Generator[X, …]`
  return annotation; non-generator → raise.

### `di/dependency_resolver.py`
- Extract the param-walk of `resolve_constructor_dependencies` into a shared
  `_dependencies_from_signature`; add `resolve_provider_dependencies(fn)` reusing
  it (no `self`, no `ClassMetadata` fallback).

### `di/container.py`
- `ServiceRegistration` gains `resource: ResourceSpec | None` and
  `provider: ProviderSpec | None`.
- `register()` reads the class-form marker (singleton-only, else raise).
- `register_provider(spec)` registers `spec.provided_type` with the provider and
  its autowired deps (singleton-only).
- `_construct(cls, reg, kwargs) -> (instance, finalizer|None)` centralizes: a
  provider (advance a sync generator; async generator → "use aget"); else
  `cls(**kwargs)` + optional CM `__enter__` / close finalizer. `_resolve_singleton`
  records the finalizer under `_resource_lock` right after caching.
- `_Finalizer(frozen)`: `key`, `close|None`, `aclose|None`, `label`; `is_async`.
  Sync-gen/async-gen closers swallow the expected `StopIteration`/`StopAsyncIteration`.
- `aget(cls)`: overrides + warm cache; async-generator provider → await first
  yield under the singleton lock; everything else → `get()`.
- `shutdown_resources()` / `ashutdown_resources()`; `__enter__`/`__exit__`/
  `__aenter__`/`__aexit__`; `reset()` clears finalizers. Torn-down singletons are
  dropped so a later `get()` rebuilds.

### `decorators/resource.py`
- `ResourceOptions(close="close", container=None)`.
- `Resource` dual-mode: bare on a class/function, or `@Resource(close=…)`. Class →
  attach `ResourceSpec` marker; function → `container.register_provider(...)`.
  Lowercase alias `resource = Resource`.

### Exports & errors
- `ResourceTeardownError(InitoError)`.
- Export `Resource`/`resource`/`ResourceOptions` from `inito` and `inito.di`.
- Docs: DI-page "Resources (lifecycle & teardown)" section + pieces-table row;
  README DI section + concepts table + TOC; `reference/dependency-injection.md`;
  `docs/index.md`. CHANGELOG `[Unreleased]`; `dev/` tracking.

## Verification
Dep-free tests (`tests/di/test_resources.py`; async driven by `asyncio.run`, no
plugin): sync `close()` called LIFO on `shutdown_resources()`/`with container`;
custom close name; CM `__enter__`/`__exit__`; async `aclose` via
`ashutdown_resources()`/`async with`; sync `shutdown_resources()` with an async
resource raises; sync generator provider (autowired dep + post-yield cleanup);
async generator provider via `aget`; teardown errors aggregated but every
resource still closed; torn-down singleton rebuilds; non-singleton `@Resource`
and non-generator `@Resource` function raise; `reset()` drops finalizers. Then
the full gate (ruff/format/mypy strict/pytest ≥95%/docs -W) and a Python 3.9 run.
