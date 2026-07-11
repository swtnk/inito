# @Data

The all-in-one decorator: one line gives a class a constructor, `__repr__`,
`__eq__`, `__hash__`, and a getter/setter per field.

## The problem it solves

A class that just holds a few fields still needs a constructor, a readable
`repr`, value-based equality and hashing, and `get_x`/`set_x` accessors.
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
| `__init__` | required fields first, then defaulted ones — the usual Python ordering |
| `__repr__` | `ClassName(field=value, ...)` for every field |
| `__eq__` | value equality; different classes compare `NotImplemented` |
| `__hash__` | hashes the tuple of all field values |
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

```python
@Data(frozen=True)             # immutable value object, no setters
@Data(include_setters=False)   # read-only accessors, but still mutable via obj.x = ...
@Data(include_getters=False)   # no getters
```

`frozen=True` and `@Value` both give a genuinely immutable class; `@Value`
is the more descriptive choice when immutability is the point (see
[@Value](value.md)).

## Notes & gotchas

- **Mutable defaults** (a `list`/`dict`/`set`) need `dataclasses.field`,
  which inito reads only from a real dataclass — stack `@dataclass`:

  ```python
  from dataclasses import dataclass, field

  @Data
  @dataclass
  class Config:
      tags: list = field(default_factory=list)   # a fresh list per instance
  ```

- **Your own methods are untouched.** `@Data` only attaches the members
  listed above; any other method you define is left alone. It *will*
  overwrite a method it generates (e.g. a hand-written `__repr__`) since it
  attaches its version last.
- **`include_setters=False` is not immutability** — it only omits the
  `set_x` helpers; `obj.x = 5` still works. Use `frozen=True` (or `@Value`)
  to actually forbid mutation.

## See also

- [@Value](value.md) — `@Data` without setters, always immutable.
- [Accessors](accessors.md), [@ToString](to-string.md),
  [@EqualsAndHashCode](equals-and-hash-code.md) — the atomic pieces `@Data`
  bundles.
- [API reference](../reference/index.md)
