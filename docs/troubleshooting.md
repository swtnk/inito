# Troubleshooting

## `FrozenInstanceError` when calling a setter on a frozen instance

```python
from dataclasses import dataclass
from inito import Data


@Data
@dataclass(frozen=True)
class Point:
    x: int
    y: int


point = Point(1, 2)   # works — @dataclass(frozen=True) is innermost
point.set_x(5)         # raises dataclasses.FrozenInstanceError - expected
point.x = 5            # also raises - expected
```

This is expected, not a bug: generated setters remain plain attribute
assignment, so post-construction mutation on a frozen dataclass correctly
still fails — only *construction itself* is exempted from the frozen
check (for an immutable class, generated constructors use
`object.__setattr__` internally, the same technique a real frozen
dataclass's own `__init__` uses).

**Stacking order matters:** put `@dataclass(frozen=True)` **innermost**
(closest to the class), as above. In the reverse order —
`@dataclass(frozen=True)` on the *outside* of `@Data` — construction itself
raises `FrozenInstanceError`, because inito generates its constructor
before the outer `@dataclass` installs the frozen `__setattr__` and so
can't know to bypass it. Use the innermost order, or `@Value` /
`@Data(frozen=True)` (which need no stacking), for an immutable class.

## `FrozenInstanceError` from `@Value`/`@Data(frozen=True)` alone (no `@dataclass` needed)

```python
from inito import Value


@Value
class Point:
    x: int
    y: int


point = Point(1, 2)
point.x = 5   # raises dataclasses.FrozenInstanceError - expected
```

Also expected: `@Value` and `@Data(frozen=True)` are genuinely immutable
on their own, generating a `__setattr__`/`__delattr__` pair that
unconditionally raises `dataclasses.FrozenInstanceError` — no
`@dataclass(frozen=True)` stacking required. This applies regardless of
how the instance was built (`Point(1, 2)`, `@Builder`'s `build()`,
`.to_builder()`, ...), since every inito constructor assigns fields via
`object.__setattr__`, bypassing the generated `__setattr__` only for
that one internal call.

## `AnnotationResolutionError` on a field annotation

```python
from inito import Data


@Data
class Sample:
    value: DoesNotExist   # raises AnnotationResolutionError - DoesNotExist isn't defined
```

`inito` resolves annotations eagerly, once, at decoration time (the core
performance rule: reflection happens once, at decoration time, never
later). If a name in a field's annotation genuinely isn't defined
anywhere reachable, this is the correct, expected error — fix the
annotation or make sure the referenced name is actually importable/defined
before the class is decorated.

**Self-referential fields work fine** (e.g. a linked-list `next: Node`) —
this used to be a limitation but no longer is; see the
[README](https://github.com/swtnk/inito#self-referential-fields) for how.

## mypy flags `user.get_name()`, `Point.builder()`, etc. as unknown attributes

Enable inito's bundled mypy plugin — without it, mypy has no way to know
about members attached via `setattr` at decoration time:

```toml
[tool.mypy]
plugins = ["inito.typing.mypy_plugin"]
```

With the plugin enabled, `mypy --strict` correctly infers the real
`__init__` signature, `get_x`/`set_x` accessor types, and the full
`.builder()`/`Builder`/`.to_builder()` chain for every decorator. One
cosmetic quirk: `reveal_type()` on a `Builder` instance itself may show a
doubled qualname (e.g. `Point.Point.Builder`) due to how mypy formats
synthetic nested classes — this doesn't affect type-checking correctness,
only that one debug-output string.

## pyright still flags `get_x`/`set_x`/`@Builder` members as unknown

pyright has no third-party mypy-plugin equivalent, so the plugin above
doesn't help it. This is a real, currently-unresolved gap — your code runs
correctly regardless, but pyright can't verify it statically. See the
[README's known limitations section](https://github.com/swtnk/inito#known-limitation-pyright-doesnt-see-most-generated-members)
for more, and `dev/history.md` Phase 17 for what closing this would require.

**Exception:** `@Data`, `@AllArgsConstructor`, and `@Value`'s constructors
*are* correctly typed under pyright too, via a `.pyi` stub marked with the
standard `typing.dataclass_transform` (PEP 681) — no inito-specific plugin
needed there, since both tools understand this marker natively. This
doesn't extend to `@NoArgsConstructor`/`@RequiredArgsConstructor`, whose
real constructor signatures can't be expressed by `dataclass_transform`
without misrepresenting them (see the README section above for why).

## `ValueError: '<field>' in __slots__ conflicts with class variable`

This is a native Python error, not an `inito` one — it happens at class-body
execution time, before any decorator runs, if you combine `__slots__` with a
class-level default for the same name:

```python
class Point:
    __slots__ = ("x",)
    x: int = 0   # raises ValueError - unrelated to inito
```

Slotted classes with *required* fields (no class-level default) work fine
with `inito`.

## `KeyError` from `GeneratorRegistry.get`

If you see `KeyError: "No generator registered for capability '...'"`,
you're calling internal machinery directly (`core.attach.attach_capability`)
with a capability name that was never registered. This shouldn't happen
through any public decorator — if it does, please
[open an issue](https://github.com/swtnk/inito/issues).

## `CircularDependencyError` from a DI `Container`

```python
from inito import Service, default_container


@Service
class A:
    def __init__(self, b: "B"):
        self.b = b


@Service
class B:
    def __init__(self, a: A):
        self.a = a


default_container.get(A)   # raises CircularDependencyError: A -> B -> A
```

Two (or more) services depend on each other, directly or transitively —
the container can't build either without first building the other. The
error message lists the exact cycle in resolution order. There's no
setter-injection or lazy-proxy escape hatch in this release (that would
require exactly the kind of `__getattr__`/proxy machinery inito's core
performance rule rules out); break the cycle by extracting the shared
behavior both classes need into a third service they both depend on
instead of on each other, or by restructuring one direction of the
dependency away.

## `UnresolvableDependencyError` from a DI `Container`

Raised in two situations: (1) `container.get(cls)` was called for a `cls`
that was never `@Service`/`@Singleton`-decorated (or registered manually
via `container.register(cls)`) into that specific container; (2) one of
`cls`'s constructor parameters has a type that isn't registered *and* has
no default value, so the container has nothing to autowire and nothing to
fall back to — see
[Dependency injection: how resolution works](dependency-injection.md#how-resolution-works)
for how to fix the second case (either register the missing type, or give
the parameter a default).

## `DependencyRegistrationError` from `@Service`/`@Singleton`

Raised at decoration time if a constructor parameter has no type
annotation at all (`@Service` needs every parameter's type to build the
dependency graph — an unannotated parameter can't be autowired or checked
against a default), or if you `@Service`-decorate the same class into the
same container twice.

Stacking `@Service` on top of another inito constructor decorator works
correctly and needs no extra annotations of your own:

```python
from inito import RequiredArgsConstructor, Service


@Service
@RequiredArgsConstructor
class Repo:
    pass


@Service
@RequiredArgsConstructor
class UserService:
    repo: Repo   # a plain field annotation, not a hand-written __init__
```

`@RequiredArgsConstructor`'s (and `@AllArgsConstructor`'s/`@Data`'s/
`@NoArgsConstructor`'s) generated `__init__` carries no annotations in its
own source at all — `@Service` falls back to the `ClassMetadata` that
decorator already cached on the class (from the field's own annotation,
`repo: Repo` above) rather than requiring you to hand-write an annotated
`__init__` yourself. This only works when `@Service` is stacked directly
on a class that was itself already decorated — a plain, undecorated class
with an unannotated `__init__` parameter still needs a real annotation.

## `Container.get()`'s return type isn't `Any` under mypy/pyright

`Container.get` is a plain generic method (`def get(self, cls: type[T]) ->
T`), so `container.get(MyService)` is correctly inferred as `MyService` by
both mypy and pyright natively — no plugin hook or `.pyi` stub needed here,
unlike `get_x`/`set_x`/`@Builder`. `@Service`/`@Singleton` also never
rewrite the decorated class's constructor, so `MyService`'s own `__init__`
signature is exactly what you wrote, with no `dataclass_transform` marker
needed either.
