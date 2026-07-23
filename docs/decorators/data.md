# @Data

The all-in-one decorator: one line gives a class a constructor, `__repr__`,
`__eq__`, and a getter/setter per field (plus `__hash__` when frozen).

## The problem it solves

A class that just holds a few fields still needs a constructor, a readable
`repr`, value-based equality, and `get_x`/`set_x` accessors.
Writing those by hand is repetitive and drifts out of sync whenever a field
is added or renamed. `@Data` derives all of them from the class's
annotations, so there is nothing to keep in sync.

## Usage

```python
from inito import Data


@Data
class User:
    name: str
    email: str
    age: int = 0


user = User("Ada", "ada@example.com", age=30)
print(user)                       # User(name='Ada', email='ada@example.com', age=30)
print(user == User("Ada", "ada@example.com", 30))   # True
print(user.get_name())            # Ada
user.set_age(31)
```

## What it generates

| Member | Behaviour |
|---|---|
| `__init__` | every field, in declaration order (a required field after a defaulted one is rejected, as in `dataclasses`) |
| `__repr__` | `ClassName(field=value, ...)` for every field |
| `__eq__` | value equality; different classes compare `NotImplemented` |
| `__hash__` | **only when frozen** — a mutable `@Data` is unhashable (see below) |
| `get_<field>()` | one per field (unless `include_getters=False`) |
| `set_<field>(value)` | one per field (unless `include_setters=False` or `frozen=True`) |

Fields are the class's annotated attributes, accumulated across the MRO
(base-class fields first). `ClassVar`-annotated attributes are ignored.

## Options

`@Data` can be used bare (`@Data`) or configured (`@Data(...)`):

| Option | Default | Effect |
|---|---|---|
| `frozen` | `False` | make instances **immutable** (assignment/deletion raise `FrozenInstanceError`) and skip setters |
| `include_getters` | `True` | set `False` to omit `get_<field>()` |
| `include_setters` | `True` | set `False` to omit `set_<field>()` (does *not* make the class immutable) |
| `accessors` | `"lombok"` | accessor style: `"lombok"` (`get_x`/`set_x`), `"attr"` (none — use `obj.x`), or `"both"` (alias of `"lombok"`) |

```python
@Data(accessors="attr")        # Pythonic: no get_x/set_x, just user.name
```

`accessors="attr"` is the Pythonic choice for new code — the attribute is the
accessor. The mypy plugin honors it, so `get_`/`set_` disappear from the typed
surface too.

```python
@Data(frozen=True)             # immutable value object, no setters
@Data(include_setters=False)   # read-only accessors, but still mutable via obj.x = ...
@Data(include_getters=False)   # no getters
```

`frozen=True` and `@Value` both give a genuinely immutable class; `@Value`
is the more descriptive choice when immutability is the point (see
[@Value](value.md)).

## Notes & gotchas

- **Mutable defaults are rejected.** A shared mutable literal
  (`tags: list = []`) would be one object across every instance — the classic
  Python footgun — so InitO raises at decoration time. Use
  [`field(default_factory=...)`](../reference/decorators.md) for a fresh object
  per instance:

  ```python
  from inito import Data, field

  @Data
  class Config:
      tags: list = field(default_factory=list)   # a fresh list per instance
  ```

- **A mutable `@Data` is unhashable.** Like `dataclasses(eq=True,
  frozen=False)`, a non-frozen `@Data` sets `__hash__` to `None`, so a mutated
  instance can't silently break its own `set`/`dict` membership. Use
  `@Data(frozen=True)` or [@Value](value.md) for a hashable value type. (A
  `@Data` stacked on a frozen dataclass stays hashable.)
- **Your own methods are untouched.** `@Data` attaches only the members you did
  *not* write: a hand-written `__repr__`, `__eq__`, or `__init__` in the class
  body is left exactly as-is. (Methods synthesized by a stacked `@dataclass` are
  still taken over.)
- **`include_setters=False` is not immutability** — it only omits the
  `set_x` helpers; `obj.x = 5` still works. Use `frozen=True` (or `@Value`)
  to actually forbid mutation.

## See also

- [@Value](value.md) — `@Data` without setters, always immutable.
- [Accessors](accessors.md), [@ToString](to-string.md),
  [@EqualsAndHashCode](equals-and-hash-code.md) — the atomic pieces `@Data`
  bundles.
- [API reference](../reference/index.md)
