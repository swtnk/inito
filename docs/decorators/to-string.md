# @ToString

Generates just a `__repr__`.

## The problem it solves

A default Python `repr` (`<pkg.Point object at 0x...>`) is useless in logs
and debuggers. You often want a readable one **without** pulling in a
constructor, equality, or hashing — for example on a class that already has
its own `__init__`, or one you build with [@Builder](builder.md).
`@ToString` adds a field-listing `__repr__` and nothing else.

## Usage

```python
from inito import ToString


@ToString
class Point:
    x: int
    y: int


p = Point()
p.x, p.y = 1, 2
print(p)          # Point(x=1, y=2)
print(repr(p))    # Point(x=1, y=2)
```

It pairs especially well with `@Builder`, which builds instances directly
and does not give you a `repr` on its own:

```python
from inito import ToString, builder


@builder
@ToString
class Point:
    x: int
    y: int


print(Point.builder().x(1).y(2).build())   # Point(x=1, y=2)
```

## What it generates

A single `__repr__` rendering `ClassName(field=value, ...)` — one unrolled
f-string over every declared field, so it is the fastest of InitO's three
`repr`-capable flavors (see [Performance](../performance.md)).

## Options

None today; `@ToString` and `@ToString()` are equivalent.

## See also

- [@Data](data.md) / [@Value](value.md) — include `__repr__` as part of the
  bundle.
- [@Builder](builder.md) — commonly paired with `@ToString`.
- [@EqualsAndHashCode](equals-and-hash-code.md) — the equality/hashing
  counterpart.
- [API reference](../reference/index.md)
