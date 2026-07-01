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
[TASKS.md](./TASKS.md) for what's left: benchmarks, docs, CI hardening, and
release.

### Known limitation: static type checkers don't see generated members yet

Every generated member (`get_x`, `set_x`, `.builder()`, `.to_builder()`, the
generated constructor's parameters, ...) is attached to your class via
`setattr` at decoration time — real attributes at runtime, but invisible to
`mypy`/`pyright` today, since neither tool has a plugin for inito yet. Your
code will run correctly; `mypy --strict`/`pyright` will flag those accesses
as unknown attributes in the meantime. `attrs` and Pydantic hit the same
problem and solved it with dedicated mypy plugins — that's tracked as a
future initiative (see `TASKS.md` Phase 17), not required for this release.

### Known limitations: frozen dataclasses and self-referential fields

Stacking any inito constructor-generating decorator (`@Data`, `@Builder`,
`@AllArgsConstructor`, ...) with `@dataclass(frozen=True)` — in either
order — raises `dataclasses.FrozenInstanceError`. This is expected, not a
bug: the generated `__init__`/`build()` assign fields with plain
`self.x = value`, which correctly respects the frozen class's blocking
`__setattr__` rather than silently bypassing the immutability you asked
for. If you want inito's own frozen-style behavior, use `@Data(frozen=True)`
(which just omits setters) instead of also stacking `@dataclass(frozen=True)`.

Self-referential type hints (e.g. a linked-list `next: Node`) also aren't
supported: inito resolves annotations eagerly, once, at decoration time —
before the class's own name is bound in its module's globals — so a forward
reference to the class currently being decorated can't resolve. Forward
references to any other, already-defined class work normally.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT — see [LICENSE](./LICENSE).
