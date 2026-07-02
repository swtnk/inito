# inito

A Lombok-inspired boilerplate-elimination library for Python. `inito`
generates constructors, `repr`, equality/hashing, accessors, and fluent
builders once at class-decoration time — never at instance construction or
attribute-access time — so the generated classes perform like handwritten
ones. Zero runtime dependencies.

## Install

```bash
pip install inito
```

or

```bash
uv add inito
```

## Quick start

```python
from inito import Data


@Data
class User:
    name: str
    age: int = 0


user = User("Ada", age=30)
print(user)              # User(name='Ada', age=30)
print(user.get_name())   # Ada
user.set_age(31)
```

`@Data` also accepts options:

```python
from inito import Data


@Data(frozen=True)
class Point:
    x: int
    y: int
```

`@builder` generates a fluent, chainable builder, and composes with
`@dataclass`:

```python
from dataclasses import dataclass
from inito import builder


@builder(to_builder=True)
@dataclass
class Request:
    prompt: str
    temperature: float = 0.7


request = Request.builder().prompt("hello").build()
revised = request.to_builder().temperature(0.9).build()
```

## Type checking

inito ships a **mypy plugin** that synthesizes every generated member
(`__init__`'s real signature, `get_x`/`set_x`, `.builder()`/`Builder`/
`.to_builder()`) so `mypy --strict` sees your decorated classes correctly —
no `# type: ignore` needed. Enable it in your `pyproject.toml` or `mypy.ini`:

```toml
[tool.mypy]
plugins = ["inito.typing.mypy_plugin"]
```

The plugin is mypy-only — pyright has no third-party plugin mechanism.
`@Data` and `@AllArgsConstructor` additionally ship a `.pyi` stub marked
with the standard `typing.dataclass_transform` (PEP 681), so **pyright
also** gets a correctly-typed `__init__` for those two decorators — no
plugin needed, since this is a standard both tools understand natively.
`get_x`/`set_x` and `@Builder`'s fluent chain remain pyright's gap
regardless (see below), since `dataclass_transform` can only express a
constructor signature, not arbitrary generated methods.

## Status

Implemented today: `@Data` (constructor, `__repr__`, `__eq__`, `__hash__`,
getters, setters), `@Getter` (getters only), `@Setter` (setters only),
`@NoArgsConstructor` (no-argument constructor using field defaults),
`@AllArgsConstructor` (constructor only, every field),
`@RequiredArgsConstructor` (constructor only accepting required fields),
`@Builder`/`builder` (fluent builder, `to_builder=True` support),
`@ToString` (`__repr__` only — pairs well with `@Builder` for a readable
repr without pulling in `@Data`'s constructor/eq/hash/accessors), and
`@EqualsAndHashCode` (`__eq__`/`__hash__` only).

All of `inito.md`'s Initial Features (v1) are now implemented. See
[docs/performance.md](./docs/performance.md) for benchmarks against
handwritten classes, `dataclasses`, and `attrs`. See [TASKS.md](./TASKS.md)
for what's left: docs, CI hardening, and release.

### Known limitation: pyright doesn't see most generated members

Every generated member (`get_x`, `set_x`, `.builder()`, `.to_builder()`, the
generated constructor's parameters, ...) is attached to your class via
`setattr` at decoration time — real attributes at runtime. **mypy** sees
all of them correctly once you enable [the bundled plugin](#type-checking)
(the same approach `attrs`/Pydantic use). **pyright** has no equivalent
third-party plugin mechanism, so `get_x`/`set_x` and `@Builder`'s fluent
chain still show up as unknown attributes there — your code runs correctly
regardless, this is a pyright-only static-typing gap.

`@Data`'s and `@AllArgsConstructor`'s constructors are the exception:
**pyright does see these correctly**, via a `.pyi` stub marked with the
standard `typing.dataclass_transform` (no inito-specific plugin needed —
this is a mechanism pyright supports natively). This doesn't extend to
`@NoArgsConstructor`/`@RequiredArgsConstructor`: both were deliberately left
unmarked, since their real signatures diverge from what `dataclass_transform`
can express (`@NoArgsConstructor` truly accepts zero arguments rather than
"all fields optional"; `@RequiredArgsConstructor` excludes defaulted fields
from `__init__` entirely rather than making them optional) — applying the
marker there would make pyright silently *accept* calls the real runtime
rejects, which is worse than the current honest gap. Closing the remaining
gap for `get_x`/`set_x`/`@Builder` would need a different strategy (e.g. a
companion stub generator); tracked in `TASKS.md` Phase 17, not required for
this release.

### Composing with frozen dataclasses

Stacking any inito constructor-generating decorator (`@Data`, `@Builder`,
`@AllArgsConstructor`, ...) with `@dataclass(frozen=True)` works correctly
in either stacking order: construction succeeds, and equality/hashing work
as expected. Generated constructors assign fields via `object.__setattr__`
internally — the same technique a real frozen dataclass's own `__init__`
uses to bypass its blocking `__setattr__` for initial construction — so
this isn't a special case, it's how frozen classes are meant to be built.
Post-construction mutation (`point.set_x(5)`, `point.x = 5`) still
correctly raises `FrozenInstanceError` either way, since setters remain
plain attribute assignment — only construction is exempted from the
frozen check, not general mutation.

### Self-referential fields

Self-referential type hints (e.g. a linked-list `next: Node`) work
correctly:

```python
from __future__ import annotations
from inito import Data


@Data
class Node:
    value: int
    next: Node | None = None
```

inito resolves annotations eagerly, once, at decoration time — before the
class's own name is bound in its module's globals — so naively this would
fail to resolve. Instead, `resolve_type_hints` temporarily seeds the
module's namespace with the class itself just before resolution (and
removes it immediately after), which only affects resolution of the class
being decorated, not any other class in its inheritance chain. This is a
one-time, decoration-time-only operation with no per-instance or per-call
cost. Forward references to any other, already-defined class continue to
work normally, and a genuinely undefined name still correctly raises
`AnnotationResolutionError`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT — see [LICENSE](./LICENSE).
