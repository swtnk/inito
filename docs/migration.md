# Migration guide

## From `dataclasses`

`inito` composes with `dataclasses` rather than replacing it — `@Data`
(and every other decorator) is dataclass-aware: stack it on top of an
existing `@dataclass` and it reuses the dataclass's own field
metadata/defaults rather than re-deriving them.

```python
from dataclasses import dataclass
from inito import Getter


@Getter
@dataclass
class Point:
    x: int
    y: int
```

Reach for `inito` over plain `dataclasses` when you want:

- **Accessors** (`get_x()`/`set_x(value)`) — `dataclasses` has none.
- **A fluent builder** (`@Builder`) — `dataclasses` has none.
- **Picking capabilities individually** (`@Getter` alone, `@ToString` alone,
  ...) rather than the all-or-nothing `@dataclass(init=, repr=, eq=, ...)`
  flag surface.

Stick with plain `dataclasses` if you don't need any of the above — it's
in the standard library, and (per [Performance](performance.md)) construction
performance is within noise of `inito`.

**Known interaction:** stacking any `inito` constructor-generating decorator
with `@dataclass(frozen=True)` raises `FrozenInstanceError`, in either
stacking order — see [Troubleshooting](troubleshooting.md).

## From `attrs`

`attrs` and `inito` overlap the most: both eliminate boilerplate, both
generate real methods once at class-creation time, both have zero required
runtime overhead. The differences:

- `attrs` classes are slotted by default (`attrs.define`), which gives a
  smaller per-instance memory footprint (see
  [Performance](performance.md#results)) — `inito` doesn't generate slotted
  classes today.
- `attrs` has one flexible `@define`/`@attrs.s` entry point with many flags;
  `inito` favors many small, Lombok-named decorators
  (`@Getter`, `@ToString`, ...) you compose explicitly.
- `attrs` has mature mypy *and* pyright plugin support for its generated
  attributes; `inito` ships an equivalent [mypy plugin](installation.md#type-checking-mypy)
  but has no pyright equivalent yet (see
  [Troubleshooting](troubleshooting.md#pyright-still-flags-the-same-attributes-as-unknown)).

If you're coming from Java/Lombok and want that naming/mental model
directly in Python, `inito` will feel more familiar. If per-instance memory
or IDE type-checking of generated members matters most, `attrs` is the more
mature choice today.

## From Pydantic

Pydantic is a validation/parsing library first — it's built for validating
untrusted input (e.g. JSON from an API request) against a schema, with
coercion, custom validators, and serialization built in. `inito` does none
of that: it has no notion of "validate this value," no serialization
format support, and no runtime type checking of assigned values.

Use `inito` for plain internal data-carrier classes where you control
construction and just want less boilerplate. Use Pydantic when you're
parsing/validating external input. The two aren't mutually exclusive - it's
reasonable to use Pydantic at your API boundary and plain `inito`-decorated
classes internally.
