# DI 2.0 — Phase 1: overriding · config · qualifiers · thread-local

**Status:** not started. Detailed design → `dev/plans/di2-phase-1.md` (write
before coding). Ship as an `rc` when done.

Legend: `[x]` done · `[ ]` todo · `[~]` in progress

## 1. Test overriding
- [x] `Container.override(cls, instance)`, `override_factory(cls, factory)`,
      `clear_override(cls)`, `clear_overrides()`.
- [x] `with container.overrides({T: obj, ...}):` context manager (snapshots +
      restores overrides *and* singletons built under the override).
- [x] `get()` / `_resolve()` check overrides first (guarded so the warm path is
      unregressed); `reset()` clears overrides.
- [x] Tests (`tests/di/test_overrides.py`, 12): instance; factory; scoped context
      restore; wins over cached singleton; injected into dependents; unregistered
      target; `reset()`/`clear`.
- [ ] Docs: a "testing with overrides" section.

## 2. Config injection (zero-dep core, Pydantic optional)
- [ ] `@Config` decorator: populate a class's annotated fields from env vars
      (name mapping + prefix) and optionally a YAML/JSON file — **stdlib only**
      (no yaml dep; JSON via stdlib, YAML only if `pyyaml` present, duck-typed).
- [ ] Register a `@Config` class (or a Pydantic `BaseSettings`) as a service so
      it autowires by type into constructors.
- [ ] Type coercion from strings (int/bool/float/str) at load time, once.
- [ ] Tests: env mapping + prefix; defaults; missing-required error; Pydantic
      `BaseSettings` path (interop job); coercion.
- [ ] Docs: "configuration injection" section.

## 3. Qualifiers for multiple implementations
- [ ] `@Service(qualifier="postgres")` registers under (type, qualifier).
- [ ] Resolution: a param typed `Annotated[Repo, "postgres"]` resolves the
      qualified registration; a bare `Repo` resolves the `primary` (or the sole)
      registration.
- [ ] `@Service(qualifier=..., primary=True)` marks the default when several
      implementations of one type exist.
- [ ] Reflect-once: qualifier is read from `Annotated` metadata at registration,
      cached on `Dependency` (like `registrable`).
- [ ] Tests: two impls + qualified injection; primary selection; ambiguous
      (multiple, no primary) raises a clear error; `Annotated` unwrapping.
- [ ] Docs: "multiple implementations / qualifiers" section.

## 4. Thread-local scope
- [x] `Scope.THREAD_LOCAL` — one instance per thread (via `threading.local`).
- [x] Resolution + caching path (`_cached_instance`/`_build`); warm singleton
      path unaffected; `reset()` clears the thread-local cache.
- [x] Tests (`tests/di/test_container.py`, 3): same instance within a thread;
      distinct across threads; `reset()` clears.
- [ ] Docs: scope table update.

## Cross-cutting
- [ ] All new public names exported from `inito/__init__.py` + `di/__init__.py`.
- [ ] New exceptions (if any) in `exceptions/errors.py` under `InitoError`.
- [ ] `gate` green (ruff/format/mypy/pytest ≥95%/docs -W); 3.9 check.
- [ ] Update `dev/README.md` status + `dev/decisions.md`; `release` as `rc`.
