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


point = Point(1, 2)   # works fine, in either stacking order
point.set_x(5)         # raises dataclasses.FrozenInstanceError - expected
point.x = 5            # also raises - expected
```

This is expected, not a bug: generated setters remain plain attribute
assignment, so post-construction mutation on a frozen dataclass correctly
still fails — only *construction itself* is exempted from the frozen
check (generated constructors use `object.__setattr__` internally, the
same technique a real frozen dataclass's own `__init__` uses). If you see
`FrozenInstanceError` on the *construction* call itself rather than a
setter, please [open an issue](https://github.com/swtnk/inito/issues) —
that would be a genuine regression, not expected behavior.

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
for more, and `TASKS.md` Phase 17 for what closing this would require.

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
