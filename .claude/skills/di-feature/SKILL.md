---
name: di-feature
description: Recipe for adding a DI 2.0 capability to inito the annotation-native, zero-dependency way (test-override, config injection, qualifiers, scopes, factory, resources, etc.). Use when implementing an item from dev/roadmap.md or dev/tasks/phase-*.md. Encodes the design constraints and file-by-file wiring so they aren't re-derived.
---

# di-feature

Add a DI capability without breaking inito's guarantees.

## Constraints (check every step against `.claude/rules/python.md`)
- **Zero runtime deps.** Framework paths (Pydantic/YAML/FastAPI) are optional and
  duck-typed — never import them unconditionally.
- **Reflect once.** Any annotation/qualifier/type inspection happens at
  `@Service`/registration time and is cached on the registration (mirror how
  `Dependency.registrable` is precomputed in `di/dependency_resolver.py`).
- **Warm `Container.get()` must not regress** — keep the cached fast-path
  untouched; add work only on the cold/registration path.
- **Annotation-native surface:** drive behavior from `typing.Annotated`,
  decorator kwargs, and constructor type hints — no `Provide[]`-style markers.

## Wiring (reuse existing machinery)
1. **Design** the annotation-native API; write/refresh `dev/plans/di2-phase-N.md`.
2. **Container/resolver** (`di/container.py`, `di/dependency_resolver.py`): add
   the resolution/lifetime logic. New scope → extend `Scope` + a storage/lookup
   branch. New registration data → extend `ServiceRegistration`/`Dependency`
   (precompute at register time).
3. **Decorator** (if any) in `decorators/`: an `*Options` frozen dataclass +
   thin apply wired via `make_decorator`; export from `decorators/__init__.py`
   and top-level `inito/__init__.py`.
4. **Exceptions:** new `InitoError` subclasses in `exceptions/errors.py`.
5. **Tests** mirroring `tests/di/…`: **dependency-free** unit tests (duck-typed
   fakes) so they run on the whole 3.9–3.14 matrix; real-framework cases go in
   `tests/integration/test_framework_interop.py` (interop CI job).
6. **Docs:** update `docs/dependency-injection.md` / `docs/frameworks.md`.
7. **Track:** tick `dev/tasks/phase-N-*.md`, update `dev/README.md`, log any
   non-obvious decision in `dev/decisions.md`.
8. Run the `gate` skill; ship via the `release` skill.
