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

`@Service` also composes with `@RequiredArgsConstructor`/
`@AllArgsConstructor`/`@Data`/`@NoArgsConstructor` — a plain field
annotation (`repo: Repo`) is enough, no hand-written `__init__` required:

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

### Mixing real dependencies with plain config

A constructor parameter is only autowired if its annotated type is itself
a registered service (`repo: Repo` above). A parameter whose type isn't
registered (`retries: int`) is left alone as long as it has a default
value — the constructor's own default applies, exactly as if you'd called
it directly. If such a parameter has **no** default, resolving it raises
`UnresolvableDependencyError` — every constructor parameter must be either
autowirable or have a default, there's no third option.

### Singleton vs. transient scope

`@Singleton`/`Scope.SINGLETON` (the default) builds an instance once and
caches it — every `container.get(cls)` after the first returns the same
object. `Scope.TRANSIENT` never caches: every `get()` rebuilds the whole
subtree. One subtlety: if a transient service is itself a dependency of a
singleton, it's only ever built once — at the singleton's first
resolution — since the singleton itself is cached. This is standard DI
behavior, not an inito-specific quirk, but it's easy to assume "transient"
always means "fresh every time" when it actually means "fresh every time
*it's resolved directly*."

### Thread-safety and process-safety

Concurrent first-access to a singleton, from multiple threads, is safe:
`Container` uses double-checked locking (a lazily-created lock per
registered class) around singleton construction, so exactly one thread
builds the instance and every other concurrent caller gets that same
object back — none of them silently ends up with a second, independent
instance, and construction never runs twice. Dependencies are resolved
*before* a service's construction lock is taken, so no thread ever holds
two locks at once: a cyclic graph resolved concurrently from opposite ends
raises `CircularDependencyError` cleanly rather than deadlocking. This
costs nothing on the already-resolved (warm) path: no lock is touched at
all once a singleton is cached, so post-first-resolution `get()` calls and
attribute access on resolved instances remain exactly as cheap as without
any locking (see [Performance](performance.md)'s dependency-injection
section for the measured numbers).

A `Container` is always **process-local** — this isn't an inito
limitation, it's true of any in-memory Python object. Each OS process
(each `multiprocessing.Process`, each pre-fork web worker, ...) gets its
own independent copy of `default_container` and therefore its own,
separate singleton instances. If you need one value truly shared across
processes, that requires external state (a database, a file, shared
memory) — no pure in-process container can provide it.

### `@Inject` has a real, per-call cost

Every other inito decorator generates real methods once, at decoration
time, with zero added cost afterward. `@Inject` is the one exception: it
wraps a **function** (typically a composition-root entry point like
`main()`, not a hot-path method), and resolving its unfilled,
container-registered parameters happens on **every call** — a
`container.get()` per unfilled parameter, not a full re-reflection (the
function's signature and type hints are inspected once, at decoration
time, and cached on the wrapper). This is architecturally unavoidable for
a container whose registrations can grow over time, and is consistent
with how other DI frameworks treat this exact boundary. Once you have a
resolved object in hand — from `@Inject`, `container.get()`, or plain
construction — using it is ordinary Python with no DI-related overhead at
all; see [docs/performance.md](performance.md) for benchmark numbers.

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
