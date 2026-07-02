# Quick start

## @Data: the all-in-one decorator

```python
from inito import Data


@Data
class User:
    name: str
    age: int = 0


user = User("Ada", age=30)
print(user)              # User(name='Ada', age=30)
print(user == User("Ada", 30))   # True
print(user.get_name())   # Ada
user.set_age(31)
```

`@Data` generates a constructor, `__repr__`, `__eq__`, `__hash__`, and
`get_<field>()`/`set_<field>(value)` accessors for every declared field —
required fields first, defaulted fields after, matching normal Python
parameter ordering rules.

### Options

```python
@Data(frozen=True)             # omit setters
@Data(include_getters=False)   # omit getters
@Data(include_setters=False)   # omit setters, keep getters
```

## @Value: an immutable-style data class

```python
from dataclasses import dataclass
from inito import Value


@Value
@dataclass(frozen=True)
class Point:
    x: int
    y: int


point = Point(1, 2)
print(point)              # Point(x=1, y=2)
print(point.get_x())      # 1
```

`@Value` is `@Data` without setters: constructor, `__repr__`, `__eq__`,
`__hash__`, and `get_<field>()` accessors — no `set_<field>(value)` is ever
generated. Stack with `@dataclass(frozen=True)` for genuine attribute-write
immutability; on its own `@Value` only omits setters, it doesn't block
direct attribute assignment (`point.x = 5` would still work without the
`@dataclass(frozen=True)` stack).

## Composing atomic decorators

Every capability `@Data` bundles is also available on its own, so you can
pick exactly what you need:

```python
from inito import AllArgsConstructor, EqualsAndHashCode, Getter, Setter, ToString


@AllArgsConstructor
@ToString
@EqualsAndHashCode
@Getter
@Setter
class User:
    name: str
    age: int
```

This is functionally equivalent to `@Data` — each atomic decorator resolves
the exact same underlying generator `@Data` uses internally, so there's no
duplicated logic, only a more explicit spelling.

## @Builder: a fluent builder

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

`@builder` works standalone on a plain class too — it doesn't require
`@dataclass` or `@Data`, since `build()` constructs instances directly
rather than depending on `__init__`. Pair it with `@ToString` if you also
want a readable `repr` without pulling in `@Data`'s constructor/eq/hash:

```python
from inito import ToString, builder


@builder
@ToString
class Point:
    x: int
    y: int


point = Point.builder().x(1).y(2).build()
print(point)   # Point(x=1, y=2)
```

See [API reference](api.md) for the full decorator list and
[Examples](examples.md) for a runnable script per decorator.
