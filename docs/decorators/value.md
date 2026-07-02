# @Value

An immutable data class: like [@Data](data.md), but with no setters and
genuine immutability.

## The problem it solves

Value objects — money, coordinates, identifiers, configuration snapshots —
should be immutable: once built, they never change, so they are safe to
share, cache, and use as dict keys or set members. Doing this by hand means
a constructor, `repr`, `eq`/`hash`, *and* a blocking `__setattr__`.
`@dataclass(frozen=True)` covers the immutability but gives no accessors and
still requires you to opt in each time. `@Value` is the single, descriptive
decorator for "this is an immutable value".

## Usage

```python
from dataclasses import FrozenInstanceError
from inito import Value


@Value
class Money:
    amount: int
    currency: str = "USD"


price = Money(500)
print(price)                       # Money(amount=500, currency='USD')
print(price == Money(500, "USD"))  # True
print(price.get_currency())        # USD  (getters, but never setters)

try:
    price.amount = 0               # immutable
except FrozenInstanceError:
    print("cannot mutate a @Value")

usable_as_key = {Money(500): "five dollars"}   # hashable
```

## What it generates

Constructor, `__repr__`, `__eq__`, `__hash__`, and `get_<field>()` — the
same as `@Data` **minus setters** — plus a blocking `__setattr__`/
`__delattr__` pair. Any attribute assignment or deletion after construction
raises `dataclasses.FrozenInstanceError`. No `@dataclass(frozen=True)`
stacking is needed.

## Options

| Option | Default | Effect |
|---|---|---|
| `include_getters` | `True` | set `False` to omit `get_<field>()` |

`@Value` never generates setters — that is the point — so there is no
`include_setters` option.

## `@Value` vs `@Data(frozen=True)`

They produce the same runtime behaviour (immutable, setter-free). Prefer
`@Value` when immutability is the class's defining trait — it reads as
intent — and `@Data(frozen=True)` when you have a `@Data` class you want to
lock down via an option.

## Notes & gotchas

- Construction still succeeds because the generated constructor writes
  fields via `object.__setattr__`, bypassing the blocking `__setattr__` —
  exactly how a frozen `dataclass` builds itself. Everything *after*
  construction is frozen.
- A non-frozen class uses a plain `self.x = x`, which is faster; the
  immutable path costs a little more to construct but reads at the same
  speed. See [Performance](../performance.md).

## See also

- [@Data](data.md) — the mutable, setter-included counterpart.
- [Composing with frozen dataclasses](../troubleshooting.md) — stacking
  order rules if you combine inito with `@dataclass(frozen=True)`.
- [API reference](../reference/index.md)
