# @EqualsAndHashCode

Generates `__eq__` and `__hash__` together.

## The problem it solves

By default two instances are equal only if they are the *same* object.
For a value-like class you usually want **value equality** — equal if all
fields are equal — and a matching `__hash__` so instances can live in sets
and dict keys. Python couples the two (defining `__eq__` without `__hash__`
makes a class unhashable), which is easy to get wrong by hand.
`@EqualsAndHashCode` generates both, consistently, from the class's fields —
without a constructor or `repr`.

## Usage

```python
from inito import EqualsAndHashCode


@EqualsAndHashCode
class Version:
    major: int
    minor: int


a, b = Version(), Version()
a.major, a.minor = 1, 4
b.major, b.minor = 1, 4
print(a == b)             # True  (value equality)
print(hash(a) == hash(b)) # True
print({a, b})             # a single-element set — a and b are equal & hash equal
```

## What it generates

| Member | Behaviour |
|---|---|
| `__eq__` | compares the tuple of all field values; a different class yields `NotImplemented` |
| `__hash__` | `hash()` of the tuple of all field values |

The two are always generated together — matching Python's own hash/eq
contract (a class that overrides `__eq__` must define `__hash__` to stay
hashable).

## Options

None today; `@EqualsAndHashCode` and `@EqualsAndHashCode()` are equivalent.

## Notes & gotchas

- Equality is class-exact: `a == b` is only considered when
  `a.__class__ is b.__class__`, otherwise it returns `NotImplemented` (so a
  subclass and base instance are never accidentally "equal").
- Because it generates `__hash__`, instances stay hashable even though they
  are mutable — the hash reflects the *current* field values, so avoid
  mutating an instance while it is stored in a set or used as a dict key.

## See also

- [@Data](data.md) / [@Value](value.md) — include eq/hash in the bundle.
- [@ToString](to-string.md) — the `repr` counterpart.
- [API reference](../reference/index.md)
