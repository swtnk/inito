# Troubleshooting

## `FrozenInstanceError` when stacking with `@dataclass(frozen=True)`

```python
from dataclasses import dataclass
from inito import Data


@Data
@dataclass(frozen=True)
class Point:
    x: int
    y: int


Point(1, 2)   # raises dataclasses.FrozenInstanceError
```

This happens in either stacking order (`@Data` then `@dataclass(frozen=True)`,
or the reverse) and is expected, not a bug: the generated `__init__`
(and `@Builder`'s `build()`) assign fields with plain `self.x = value`,
which correctly respects the frozen class's blocking `__setattr__` rather
than silently bypassing the immutability you asked for.

**Fix:** don't stack both. Use `@Data(frozen=True)` on its own (which just
omits setter generation) if you want inito's frozen-style behavior, or use
plain `@dataclass(frozen=True)` on its own if you want Python's native
frozen semantics.

## `AnnotationResolutionError` on a self-referential field

```python
from __future__ import annotations
from inito import Data


@Data
class Node:
    value: int
    next: Node | None = None   # raises AnnotationResolutionError
```

`inito` resolves annotations eagerly, once, at decoration time — before the
class's own name is bound in its module's globals (the core performance
rule: reflection happens once, at decoration time, never later). A
self-referential forward reference therefore can't resolve, unlike
`dataclasses`, which only resolves annotations lazily if you explicitly
call `typing.get_type_hints()` yourself.

**Fix:** there isn't currently a workaround that preserves eager resolution
for genuinely self-referential fields. If you need a linked structure, keep
the self-referential field un-annotated for `inito`'s purposes, or manage
that field outside the decorator-generated constructor.

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

## pyright still flags the same attributes as unknown

pyright has no third-party mypy-plugin equivalent, so the plugin above
doesn't help it. This is a real, currently-unresolved gap — your code runs
correctly regardless, but pyright can't verify it statically. See the
[README's known limitations section](https://github.com/swtnk/inito#known-limitation-pyright-doesnt-see-generated-members)
for more, and `TASKS.md` Phase 17 for what closing this would require.

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
