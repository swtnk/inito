# DI 2.0 — Phase 1: overriding · config · qualifiers · thread-local

**Status:** not started. Detailed design → `dev/plans/di2-phase-1.md` (write
before coding). Ship as an `rc` when done.

Legend: `[x]` done · `[ ]` todo · `[~]` in progress

## 1. Test overriding
- [ ] `Container.override(cls, instance_or_factory)` and `clear_override(cls)` /
      `clear_overrides()`.
- [ ] `with container.overrides({T: obj, ...}):` context manager (auto-restores).
- [ ] `get()` / `_resolve()` check overrides first (before singleton cache).
- [ ] Tests: override an instance; override a factory; scoped context restores;
      override wins over a cached singleton; interaction with `reset()`.
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
- [ ] `Scope.THREAD_LOCAL` — one instance per thread (via `threading.local`).
- [ ] Resolution + caching path for thread-local; warm path unaffected.
- [ ] Tests: distinct instances across threads; same instance within a thread.
- [ ] Docs: scope table update.

## Cross-cutting
- [ ] All new public names exported from `inito/__init__.py` + `di/__init__.py`.
- [ ] New exceptions (if any) in `exceptions/errors.py` under `InitoError`.
- [ ] `gate` green (ruff/format/mypy/pytest ≥95%/docs -W); 3.9 check.
- [ ] Update `dev/README.md` status + `dev/decisions.md`; `release` as `rc`.
