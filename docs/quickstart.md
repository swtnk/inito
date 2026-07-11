# Quick start

A five-minute tour of inito: install it, meet the all-in-one `@Data`, the
immutable `@Value`, the fluent `@Builder`, dependency injection, and how to
compose the atomic decorators yourself. Every example is copy-paste runnable.

```bash
pip install inito       # or:  uv add inito
```

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
@Data(frozen=True)             # genuinely immutable: no setters, assignment/deletion raise
@Data(include_getters=False)   # omit getters
@Data(include_setters=False)   # omit setters, keep getters (not immutable - direct assignment still works)
```

## @Value: a genuinely immutable data class

```python
from inito import Value


@Value
class Point:
    x: int
    y: int


point = Point(1, 2)
print(point)              # Point(x=1, y=2)
print(point.get_x())      # 1
point.x = 5                # raises dataclasses.FrozenInstanceError
```

`@Value` is `@Data` without setters, and genuinely immutable: constructor,
`__repr__`, `__eq__`, `__hash__`, and `get_<field>()` accessors — no
`set_<field>(value)` is ever generated, and attribute assignment/deletion
always raise `dataclasses.FrozenInstanceError` after construction. No
`@dataclass(frozen=True)` stacking is needed — `@Value` enforces this
itself. `@Data(frozen=True)` gets the same real enforcement.

## Dependency injection

```python
from inito import Inject, Service, Singleton


@Singleton
class Repo:
    def __init__(self) -> None:
        self.ages = {"Ada": 30}


@Service
class UserService:
    def __init__(self, repo: Repo, retries: int = 3) -> None:
        self.repo = repo
        self.retries = retries


@Inject
def main(service: UserService) -> None:
    print(service.repo.ages["Ada"])   # 30


main()
```

`@Service` registers a class's constructor dependency types into a
`Container` (`default_container` unless you pass `container=`) **at
decoration time only** — it never instantiates anything and never mutates
the class, so `UserService(repo=Repo(), retries=5)` still works exactly
like an ordinary Python class. Dependency graphs are resolved and built
lazily, bottom-up, on the first `container.get(cls)`/`@Inject`-resolved
call. `@Singleton` is sugar for `@Service(scope=Scope.SINGLETON)` — the
default scope; pass `@Service(scope=Scope.TRANSIENT)` for a fresh instance
on every resolution instead.

`@Service` also composes with the [constructor
decorators](decorators/constructors.md) — a plain field annotation
(`repo: Repo`) is enough, no hand-written `__init__` required:

```python
from inito import RequiredArgsConstructor, Service


@Service
@RequiredArgsConstructor
class Repo:
    pass


@Service
@RequiredArgsConstructor
class UserService:
    repo: Repo
```

That is the tour. The **[Dependency injection guide](dependency-injection.md)**
covers the rest in depth: autowiring vs. plain config, singleton vs.
transient scope, custom containers, the error types, and the thread-safety
and performance guarantees.

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

See [API reference](reference/index.md) for the full decorator list and
[Examples](examples.md) for a runnable script per decorator.
