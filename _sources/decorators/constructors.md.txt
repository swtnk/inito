# Constructors

Three constructor-only decorators — `@NoArgsConstructor`,
`@AllArgsConstructor`, and `@RequiredArgsConstructor` — that generate an
`__init__` and nothing else. They are the right choice when you want a
constructor but *not* the rest of what [@Data](data.md) provides (no `repr`,
no `eq`/`hash`, no accessors).

## The problem they solve

Different classes want different constructor shapes: a form with no
arguments (everything defaulted), a form taking every field, or a form
taking only the fields that *must* be supplied. Writing each by hand is
mechanical and easy to get out of order. These three decorators generate
exactly the shape you name, deriving parameters from the class's fields.

## @AllArgsConstructor

An `__init__` taking **every** field — required fields first, defaulted
fields after (standard Python ordering).

```python
from inito import AllArgsConstructor


@AllArgsConstructor
class Point:
    x: int
    y: int
    label: str = "origin"


p = Point(1, 2)                 # label defaults to "origin"
q = Point(1, 2, "corner")
# __init__ signature: (self, x, y, label='origin')
```

## @RequiredArgsConstructor

An `__init__` taking **only the fields without a default**. Defaulted fields
are set to their default and are *not* constructor parameters — so the
constructor asks only for what it genuinely needs.

```python
from inito import RequiredArgsConstructor


@RequiredArgsConstructor
class Connection:
    host: str                   # required -> a parameter
    port: int                   # required -> a parameter
    timeout: float = 30.0       # has a default -> NOT a parameter


c = Connection("localhost", 5432)
print(c.timeout)                # 30.0
# __init__ signature: (self, host, port)   -- timeout is excluded
```

`@RequiredArgsConstructor` pairs naturally with
[dependency injection](../dependency-injection.md): a field annotation is all
`@Service` needs to autowire it.

## @NoArgsConstructor

An `__init__` taking **no arguments**; every field is set to its default.

```python
from inito import NoArgsConstructor


@NoArgsConstructor
class Settings:
    host: str = "localhost"
    port: int = 8080


s = Settings()                  # (self) -- no parameters
print(s.host, s.port)           # localhost 8080
```

**Every field must have a default** — otherwise there would be nothing to
assign a required field. A field without a default raises
`InvalidFieldDefinitionError` at decoration time (fail fast, at import),
not later at construction.

## At a glance

| Decorator | `__init__` parameters | Defaulted fields |
|---|---|---|
| `@AllArgsConstructor` | every field | become optional parameters |
| `@RequiredArgsConstructor` | required fields only | set to their default, not parameters |
| `@NoArgsConstructor` | none | set to their default (all fields must have one) |

## Notes & gotchas

- These generate **only** `__init__`. Add [@ToString](to-string.md),
  [@EqualsAndHashCode](equals-and-hash-code.md), or the
  [accessors](accessors.md) alongside if you want them — or just use
  [@Data](data.md), which is `@AllArgsConstructor` plus all of those.
- **Typing:** `@AllArgsConstructor` ships a `dataclass_transform` stub, so
  both mypy and pyright infer its `__init__` signature.
  `@NoArgsConstructor`/`@RequiredArgsConstructor` are deliberately *not*
  marked, because `dataclass_transform` can't express "zero args" or
  "defaulted fields excluded" without misleading the checker — enable the
  [mypy plugin](../installation.md#type-checking-mypy) for those two.

## See also

- [@Data](data.md) — bundles `@AllArgsConstructor` with repr/eq/hash/accessors.
- [@Builder](builder.md) — a fluent alternative to a many-argument constructor.
- [Dependency injection](../dependency-injection.md) — `@Service` on top of
  `@RequiredArgsConstructor`.
- [API reference](../reference/index.md)
