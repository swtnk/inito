# @Getter and @Setter

Lombok-style accessors: a `get_<field>()` and/or `set_<field>(value)` for
every declared field.

## The problem it solves

Sometimes you want accessors — for a uniform API, or to match code that
expects `get_x()`/`set_x()` — without the rest of what `@Data` provides
(no generated constructor, no `__eq__`/`__hash__`). `@Getter` and `@Setter`
add just the accessors, and nothing else.

## Usage

```python
from inito import Getter, Setter


@Getter
@Setter
class Point:
    x: int
    y: int


p = Point()
p.x, p.y = 1, 2
print(p.get_x(), p.get_y())   # 1 2
p.set_x(10)
print(p.get_x())              # 10
```

Use them independently, too: `@Getter` alone for read-only accessors,
`@Setter` alone for write-only mutators.

## What it generates

| Decorator | Generates |
|---|---|
| `@Getter` | `get_<field>(self)` returning `self.<field>`, one per field |
| `@Setter` | `set_<field>(self, value)` assigning `self.<field> = value`, one per field |

Neither generates a constructor, so you provide instances however you like
— a hand-written `__init__`, a stacked constructor decorator, or setting
attributes directly (as above). Fields are the annotated attributes across
the MRO; `ClassVar` attributes are skipped.

## Options

Neither decorator takes options today; both support the bare and called
forms (`@Getter` and `@Getter()`).

## Notes & gotchas

- These are plain methods — `get_x()` is exactly `return self.x`, with no
  descriptor magic — so they run at handwritten speed and never interfere
  with normal attribute access (`p.x` still works).
- To get accessors *and* a constructor and `repr`/`eq`/`hash`, reach for
  [@Data](data.md) instead of stacking every atomic decorator.

## See also

- [@Data](data.md) — bundles accessors with a constructor, `repr`, and
  `eq`/`hash`.
- [Constructors](constructors.md) — pair accessors with a generated
  constructor.
- [API reference](../api.md)
