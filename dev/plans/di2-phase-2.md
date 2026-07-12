# DI 2.0 — Phase 2: `Factory[T]` (call-time arguments)

## Context

InitO's DI builds a service once, autowiring *all* its constructor parameters
from the container. But some objects must be built **on demand, with runtime
data** the container can't know — a report for a given title, a session for a
given request — while still autowiring the dependencies the container *does*
have. `dependency-injector` solves this with a `Factory` provider; InitO's
annotation-native equivalent is injecting a `Factory[T]`.

**Goal:** let a service depend on `Factory[Widget]` and call it —
`self.make_widget(title="Sales")` — to build a fresh `Widget` per call, with
registered-typed parameters autowired and the rest supplied at call time.

**Decisions (this session):** the target need **not** be registered (prototype
factory); **call-time keyword args win** (they override autowiring for that
param), every other registered-typed param is autowired, and anything left falls
to the constructor's own default or a natural missing-argument error. Keyword-only
for v1. Reflect-once and zero-dependency preserved.

## Design

### `Factory[T]` — the public type (`di/factory.py`)
```python
class Factory(Generic[T]):
    def __call__(self, **kwargs: Any) -> T: ...   # injected object is callable, returns T
```
`Factory` is the annotation marker (`make: Factory[Widget]`) and the static type
(mypy/pyright see `make(...)` returning `Widget` — no plugin needed). The value
the container injects is a private `_BoundFactory(Factory[T])`.

### Detection, cached at registration (`di/dependency_resolver.py`)
- Add `factory_target(type_hint) -> type | None`: returns `X` when
  `typing.get_origin(type_hint) is Factory` (via `get_args`), else `None`.
- `Dependency` gains `factory_target` (computed in `__post_init__` alongside
  `registrable`/`qualifier`), so no per-`get()` inspection.

### Resolution (`di/container.py`)
- `_factory_plans: dict[type, dict[str, Dependency]]` — cache of a target's
  constructor plan, filled once per target via
  `resolve_constructor_dependencies(target)` (reused as-is; already reflect-once
  and errors on an unannotated parameter).
- Extract `_autowire(dependency, path) -> Any | _MISSING` from the current
  `_resolve_dependency` body: resolves a factory-target / qualifier / registered
  type / sole-or-primary subclass, and returns `_MISSING` when the type isn't
  autowirable. `_resolve_dependency` becomes: `factory_target → _make_factory`;
  else `_autowire`; else default → omit; else `UnresolvableDependencyError` (the
  qualifier-not-registered error stays a hard raise).
- `_make_factory(target)` returns `_BoundFactory(self, target, self._factory_plan(target))`.
- `_BoundFactory.__call__(**kwargs)`:
  ```
  final = dict(kwargs)                     # call-time kwargs win
  for name, dep in plan.items():
      if name in final: continue
      value = container._autowire(dep, ())
      if value is not _MISSING: final[name] = value
  return target(**final)                   # fresh instance; missing call-time arg -> TypeError
  ```
  Fresh instance every call. Nested `Factory[...]` works (a plan param may itself
  be a factory). Because the factory is lazy, a `Factory[B]` parameter can break
  an otherwise-circular graph.

### Exports & docs
- Export `Factory` from `inito` and `inito.di`.
- `docs/dependency-injection.md`: a "Factory (call-time arguments)" section
  (autowire + call-time, override, fresh-per-call, cycle-breaking) + the pieces
  table; README DI section + decorator/DI overview; `reference/dependency-injection.md`
  (`.. autoclass:: inito.Factory`).

## Files
- **New:** `src/inito/di/factory.py` (`Factory`, `_BoundFactory`).
- **Edited:** `di/dependency_resolver.py` (`factory_target` helper + `Dependency`
  field), `di/container.py` (`_factory_plans`, `_autowire`, `_make_factory`,
  `_resolve_dependency` refactor), `di/__init__.py` + `inito/__init__.py`
  (export `Factory`), `docs/*` + `README.md`, `dev/` tracking, `CHANGELOG.md`.
- **Tests:** `tests/di/test_factory.py` (dependency-free).

## Verification
1. Unit tests (dep-free): factory autowires registered deps and takes a call-time
   arg; call-time kwarg **overrides** an autowirable dep; call-time-only param
   (unregistered, no default) is required at the call and errors naturally if
   omitted; **fresh instance each call**; unregistered target works (prototype);
   nested `Factory[...]`; a `Factory` param breaks a would-be cycle; unannotated
   target parameter raises `DependencyRegistrationError` on first use.
2. `_autowire` refactor keeps every existing `tests/di/` test green (qualifiers,
   scopes, config, overrides, the parameterized-generic guard).
3. `gate` green (ruff/format/mypy strict/pytest ≥95%/docs -W); a Python 3.9 run
   (no `X | None` in a runtime-eval'd annotation; `Factory`/`Generic` fine on 3.9).
4. `mypy --strict` and pyright both infer `make(...) -> Widget` with no plugin.

## Out of scope (this pass)
- Positional call-time arguments (keyword-only for v1).
- Static type-checking of the call-time kwargs themselves (return type `T` is
  checked; the kwargs are `Any`, same limitation as other DI factories).
