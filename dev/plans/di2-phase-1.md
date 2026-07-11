# DI 2.0 — Phase 1 design: overriding · config · qualifiers · thread-local

All against `di/container.py` (`Container`, `Scope`, `ServiceRegistration`) and
`di/dependency_resolver.py` (`Dependency`, `registrable_type`). Guardrails:
zero-dep, annotation-native, reflect-once, warm `get()` unchanged.

## 1. Test overriding (smallest, ship first)
- `Container._overrides: dict[type, Callable[[], Any]]` (new).
- API: `override(cls, instance)` (returns that instance), `override_factory(cls, factory)`
  (calls per resolution), `clear_override(cls)`, `clear_overrides()`, and a
  context manager `overrides(mapping)` that snapshots + restores.
- Resolution: check `_overrides` **first**, guarded by `if self._overrides:` so
  production (no overrides) pays ~nothing. Add the guarded check at the top of
  `get()` (before the singleton fast-path) **and** `_resolve()` (so nested deps
  and cached singletons are overridden too). Overriding does not require the type
  to be registered (override any collaborator in a test).
- `reset()` also clears overrides.

## 2. Thread-local scope (small)
- `Scope.THREAD_LOCAL`. Storage: `self._thread_local = threading.local()` with a
  per-thread `cache` dict. No cross-thread lock (each thread is isolated).
- `_resolve()`: for THREAD_LOCAL, read/populate the thread-local cache. `register()`
  creates no singleton lock for it. Warm `get()` path untouched (thread-locals
  aren't in `_singletons`, so it falls through to `_resolve`).

## 3. Config injection (zero-dep core, Pydantic optional)
- `@Config(prefix="APP_", source=None)` decorator (`decorators/config.py`,
  `ConfigOptions`): at **decoration time** compute each annotated field's
  (env-key, coercer, default); attach a generated zero-arg `__init__` (via the
  sanctioned `build_function`) that reads `os.environ` (+ optional JSON file via
  stdlib `json`; YAML only if `yaml` importable, duck-typed) and coerces once.
  Env overrides file; missing + no default → `ConfigResolutionError`.
- Coercers: str/int/float/bool (+ `Optional[X]`) — a small stdlib map, computed
  once. Reflect-once honored (no per-construct annotation reads).
- Registered like any service (`@Service @Config`), autowired by type. A Pydantic
  `BaseSettings` already autowires (it loads env itself) — documented, no code.
- New exception `ConfigResolutionError(InitoError)`.

## 4. Qualifiers for multiple implementations
- `@Service(qualifier="postgres", primary=False)` — `ServiceOptions` gains
  `qualifier`/`primary`; `Container.register(cls, *, scope, qualifier, primary)`.
- New indexes: `_qualified: dict[str, type]` (name → class); `_primary: dict[type, type]`
  (base → chosen impl) — both built at registration.
- `Dependency` gains `qualifier: Optional[str]`, precomputed in
  `resolve_constructor_dependencies` from `typing.Annotated` metadata
  (`Annotated[Repo, "postgres"]`), alongside `registrable`.
- Resolution in `_resolve_dependencies`: if `dependency.qualifier` → resolve
  `_qualified[name]` (verify it subclasses the registrable base). Else if the
  registrable type isn't directly registered, look for registered subclasses:
  exactly one → use it; several → require a `primary`, else
  `AmbiguousDependencyError(InitoError)` listing candidates.
- Reflect-once: qualifier read once at registration.

## Exports & exceptions
- `di/__init__.py` + `inito/__init__.py`: `Config`, `config`, `ConfigOptions`;
  `Scope.THREAD_LOCAL` (already via Scope). New `ConfigResolutionError`,
  `AmbiguousDependencyError` in `exceptions/errors.py`.

## Tests (dependency-free where possible)
- `tests/di/test_overrides.py`; extend `tests/di/test_container.py` (thread-local,
  qualifiers, ambiguity); `tests/decorators/test_config.py` (env/prefix/coercion/
  missing, monkeypatched `os.environ`); interop: Pydantic `BaseSettings` autowire.

## Ship
Each sub-feature: implement → tests → `gate` → commit. Phase ships as `1.0.0-rc4`.
