# DI 2.0 — Phase 3: Resource lifecycle (`@Resource`)

**Status:** done. Design → `dev/plans/di2-phase-3.md`. Staged under CHANGELOG
`[Unreleased]`; ship with the next `rc`.

Legend: `[x]` done · `[ ]` todo · `[~]` in progress

## Goal
Open resources lazily and **close** them in reverse order — a DB pool, HTTP/redis
client, or session — via `@Resource` + a container that is a (sync/async) context
manager. **Decision (this session):** support **both models** — resource classes
*and* generator-provider functions.

## Work
- [x] `src/inito/di/resource.py` — `RESOURCE_ATTRIBUTE`, `ProviderKind`,
      `ResourceSpec`, `ProviderSpec`; `class_resource_spec` (close method →
      CLOSE, async iff coroutine; else `__exit__` → CM; else `__aexit__`/none →
      raise) and `provider_spec` (sync/async generator + yielded type from the
      `Iterator[X]`/`AsyncIterator[X]` return annotation). Reflect-once.
- [x] `di/dependency_resolver.py` — extracted `_dependencies_from_signature`;
      added `resolve_provider_dependencies` (no `self`, no ClassMetadata).
- [x] `di/container.py` — `ServiceRegistration.resource`/`.provider`;
      `register_provider`; `_Finalizer` (LIFO, sync/async, drops the singleton on
      teardown); `_construct`/`_construct_from_provider`/`_class_finalizer`;
      `aget` (awaits an async-generator provider's first yield);
      `shutdown_resources` (raises if an async resource is pending) /
      `ashutdown_resources`; `__enter__`/`__exit__`/`__aenter__`/`__aexit__`;
      `reset()` drops finalizers. Teardown best-effort, errors aggregated into
      `ResourceTeardownError`.
- [x] `decorators/resource.py` — `Resource`/`resource`/`ResourceOptions`
      (dual-mode: class attaches the marker, generator self-registers a provider).
- [x] `ResourceTeardownError`; exported `Resource`/`resource`/`ResourceOptions`
      from `inito`.
- [x] `tests/di/test_resources.py` (dep-free, 27; async via `asyncio.run`):
      class close LIFO / `with container`; custom close name; CM protocol; async
      `aclose` via `ashutdown_resources`/`async with`; sync shutdown rejects async;
      sync + async generator providers (autowire + cleanup, `aget`); torn-down
      singleton rebuilt; error aggregation; validation (non-singleton class,
      non-generator function, no-teardown class, async CM, bad return annotation,
      duplicate/transient provider); decorator dispatch + `aget` fast paths;
      `reset()` drops finalizers.
- [x] Docs: DI page "Resources (lifecycle & teardown)" + pieces/error rows;
      README DI section + concepts table + TOC; `reference/dependency-injection.md`;
      `docs/index.md`. CHANGELOG `[Unreleased]`.
- [x] Gate green (ruff/format/mypy strict/pytest **100%** coverage — the whole
      project, once `stubgen`/`pyright` are on PATH so their tests run instead of
      skip; defensive/version-gated branches carry `# pragma: no cover`); resource
      + factory tests pass on Python 3.9 and 3.14.

## Out of scope (→ Phase 4)
- `Scope.SCOPED` / `container.scope()`; full async dependency resolution (`aget`
  resolves an async provider's own deps through the sync path, so nesting an async
  provider as a constructor dep of a sync-built class is deferred); async
  context-manager *classes* (async construction); FastAPI `Injected[T]`.
