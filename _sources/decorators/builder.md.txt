# @Builder

Generates a fluent, chainable builder:
`Widget.builder().name("x").size(3).build()`.

## The problem it solves

A type with several optional fields leads to *telescoping constructors* —
long positional argument lists where the reader has to count commas
(`Widget("x", 3, True, None, "blue")`), or a call site cluttered with
keyword arguments. A builder makes construction readable and
order-independent, lets you set only the fields you care about, and — with
`to_builder=True` — lets you derive a modified copy of an existing instance.

## Usage

```python
from dataclasses import dataclass
from inito import Builder


@Builder(to_builder=True)
@dataclass
class HttpRequest:
    method: str
    url: str
    timeout: float = 30.0
    retries: int = 0


request = (
    HttpRequest.builder()
    .method("GET")
    .url("/users")
    .timeout(5.0)
    .build()
)

# Derive a variant without mutating the original:
with_retries = request.to_builder().retries(3).build()
```

`@Builder` works on a **plain class too** — it does not need `@dataclass` or
`@Data`, because `build()` constructs the instance directly (via `__new__`)
rather than calling `__init__`:

```python
from inito import builder


@builder
class Point:
    x: int
    y: int


point = Point.builder().x(1).y(2).build()
```

## What it generates

| Member | Behaviour |
|---|---|
| `Cls.builder()` | classmethod returning a fresh `Builder` |
| `Cls.Builder` | the nested builder class |
| `builder.<field>(value)` | fluent setter; stores the value and returns the builder |
| `builder.build()` | validates required fields are set, then returns a `Cls` instance |
| `instance.to_builder()` | (only with `to_builder=True`) a builder pre-populated from the instance |

`build()` raises `BuilderValidationError` if a **required** field (one
without a default) was never set. Defaulted fields you don't set take their
default.

## Options

| Option | Default | Effect |
|---|---|---|
| `to_builder` | `False` | also generate `instance.to_builder()` for deriving copies |
| `setter_prefix` | `""` | prefix the fluent setters, e.g. `"with_"` → `.with_name("x")` |
| `build_method_name` | `"build"` | rename the terminal method, e.g. `"create"` → `.create()` |
| `use_init` | `False` | construct via the class's own `__init__` instead of bypassing it |

```python
@Builder(setter_prefix="with_", build_method_name="create")
class Widget:
    name: str
    size: int = 1


Widget.builder().with_name("x").create()
```

### `use_init=True`: construct through the real constructor

By default `build()` is fast because it bypasses `__init__` (see the gotcha
below). When you need the class's own constructor to run — for a hand-written
`__init__` with side effects, or a validating framework model (Pydantic,
SQLAlchemy, Django) — pass `use_init=True`:

```python
from inito import Builder
from pydantic import BaseModel


@Builder(use_init=True)
class User(BaseModel):
    name: str
    age: int = 0


User.builder().name("Ada").build()               # runs Pydantic validation
User.builder().name("Ada").age("nope").build()   # raises pydantic.ValidationError
```

In this mode the builder only passes the fields you actually set, so the
constructor's own defaults and required-argument errors apply rather than
InitO's `BuilderValidationError`. See [Using InitO with your
framework](../frameworks.md) for the full guidance.

## Notes & gotchas

- **`build()` bypasses `__init__` by default.** It creates the instance with
  `cls.__new__(cls)` and assigns fields directly, so any custom `__init__`
  logic (validation, computed attributes) is *not* run by the builder. Pass
  `use_init=True` (see the option above) to construct through the real
  constructor instead, or construct normally.
- **No `repr` on its own.** `@Builder` only adds the builder machinery. Pair
  it with [@ToString](to-string.md) (or [@Data](data.md)) for a readable
  `repr`.
- Composing with a frozen class works: stack `@dataclass(frozen=True)`
  **innermost**, or use [@Value](value.md); `build()` produces the immutable
  instance correctly. See [Troubleshooting](../troubleshooting.md) for the
  stacking-order rule.

## See also

- [@ToString](to-string.md) — commonly paired for a readable `repr`.
- [Constructors](constructors.md) — the non-fluent alternative.
- [Recipes](../recipes.md) — a request/response builder example.
- [API reference](../reference/index.md)
