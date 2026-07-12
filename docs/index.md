# InitO

**A zero-dependency Python library that eliminates data-class boilerplate.**

Decorate a class and InitO writes the mechanical methods it needs — constructor,
`repr`, equality, hashing, accessors, and builders — as *real methods*, generated
once when the class is defined, never at construction or attribute-access time.
Your objects stay ordinary Python instances and run as fast as code you'd write
by hand.

```python
from inito import Data


@Data
class User:
    name: str
    age: int = 0


user = User("Ada", age=30)
print(user)                      # User(name='Ada', age=30)
print(user.get_name())           # Ada
user.set_age(31)
print(user == User("Ada", 31))   # True
```

By hand, `User` is ~20 lines of `__init__`, `__repr__`, `__eq__`, `__hash__`, and
accessors. With InitO it's the three lines above — and the generated methods are
the *same* code you'd have written, [benchmarked at parity](performance.md) with
handwritten classes and `dataclasses`.

```bash
pip install inito       # or:  uv add inito
```

Requires Python 3.9+ (tested through 3.14). No runtime dependencies.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`rocket;1.5em;sd-mr-1` Quick start
:link: quickstart
:link-type: doc

Install InitO and tour every decorator in a few minutes.
:::

:::{grid-item-card} {octicon}`light-bulb;1.5em;sd-mr-1` Concepts
:link: concepts
:link-type: doc

The boilerplate problem InitO solves — and how it stays fast.
:::

:::{grid-item-card} {octicon}`book;1.5em;sd-mr-1` User Guide
:link: user-guide
:link-type: doc

A dedicated page per decorator, plus DI, recipes, and migration.
:::

:::{grid-item-card} {octicon}`plug;1.5em;sd-mr-1` Dependency injection
:link: dependency-injection
:link-type: doc

Wire object graphs with `@Service`/`@Singleton`/`@Inject` and a `Container`.
:::

:::{grid-item-card} {octicon}`beaker;1.5em;sd-mr-1` Recipes
:link: recipes
:link-type: doc

Real-world, copy-pasteable patterns combining several decorators.
:::

:::{grid-item-card} {octicon}`code-square;1.5em;sd-mr-1` API reference
:link: reference/index
:link-type: doc

Every decorator, option, and exception, generated from the source.
:::

::::

## Why InitO

- **Real methods, generated once.** Each decorator builds true Python functions
  from your fields at decoration time and attaches them — no `__getattr__`,
  proxies, descriptors, or runtime interception. At runtime your objects are
  ordinary instances, so construction, attribute access, `==`, and `hash()` run
  at [handwritten speed](performance.md).
- **Zero runtime dependencies.** InitO imports nothing outside the standard
  library, so it installs cleanly into any project and any environment.
- **À la carte.** `@Data` is the all-in-one, but every capability is also a
  standalone decorator (`@Getter`, `@ToString`, `@EqualsAndHashCode`, ...) —
  you never pay for what you don't ask for.
- **Typed for both checkers.** A bundled [mypy
  plugin](installation.md#type-checking-mypy) makes `mypy --strict` see every
  generated member, and [`inito-stubgen`](installation.md) does the same for
  pyright / Pylance.
- **Batteries included.** Genuine immutability (`@Value`), fluent builders
  (`@Builder`), environment-backed configuration (`@Config`), and a small
  [dependency-injection](dependency-injection.md) layer — same generate-once,
  zero-dependency design throughout.

## Decorators at a glance

| Decorator | Generates | Guide |
|---|---|---|
| `@Data` | constructor · `__repr__` · `__eq__` · `__hash__` · `get_x`/`set_x` — the all-in-one | [@Data](decorators/data.md) |
| `@Value` | like `@Data` but **immutable** and setter-free | [@Value](decorators/value.md) |
| `@Getter` / `@Setter` | `get_x()` / `set_x(value)` accessors only | [Accessors](decorators/accessors.md) |
| `@ToString` | `__repr__` only | [@ToString](decorators/to-string.md) |
| `@EqualsAndHashCode` | `__eq__` + `__hash__` only | [@EqualsAndHashCode](decorators/equals-and-hash-code.md) |
| `@NoArgsConstructor` · `@AllArgsConstructor` · `@RequiredArgsConstructor` | an `__init__` and nothing else | [Constructors](decorators/constructors.md) |
| `@Builder` / `builder` | fluent `Cls.builder().x(1).build()`, optional `.to_builder()` | [@Builder](decorators/builder.md) |
| `@Config` | load fields from environment variables, autowired by type | [@Config](decorators/config.md) |
| `@Service` / `@Singleton` / `@Inject` | dependency injection via a `Container` | [DI](dependency-injection.md) |

Every PascalCase decorator has a lowercase alias (`data`, `builder`, `value`, …)
bound to the same object — use whichever reads better.

## Dependency injection

A small, lazy, thread-safe [DI layer](dependency-injection.md): declare a class's
dependencies as fields, and a `Container` wires them — no markers, no provider
objects. `@RequiredArgsConstructor` even writes the constructor for you.

```python
from inito import Inject, RequiredArgsConstructor, Service, Singleton


@Singleton
class Database:
    rows = {1: "Ada"}


@Service
@RequiredArgsConstructor
class UserService:
    db: Database                      # autowired from the container


@Inject
def main(service: UserService) -> None:
    print(service.db.rows[1])         # Ada


main()
```

It also supports [scopes](dependency-injection.md#scopes) (singleton, transient,
thread-local), [qualifiers](dependency-injection.md#multiple-implementations-qualifiers)
for multiple implementations, [config injection](dependency-injection.md#configuration-injection),
[factories](dependency-injection.md#factory-call-time-arguments) for on-demand
construction with call-time arguments,
[resource lifecycle](dependency-injection.md#resources-lifecycle-and-teardown) with
ordered teardown (`@Resource`, `with container`), and
[test overrides](dependency-injection.md#testing-with-overrides).

## Type checking

InitO attaches members at decoration time, so type-checkers need a hint — and it
ships one for both. Enable the [mypy plugin](installation.md#type-checking-mypy)
for `mypy --strict`, or run [`inito-stubgen`](installation.md) to generate `.pyi`
stubs that give **pyright / Pylance** the same full visibility.

## Works with your framework

Zero dependencies and plain methods on plain classes mean InitO drops into any
project. On a Pydantic / SQLAlchemy / Django **model**, use the additive
decorators and let the framework own construction; the DI layer resolves safely
from `async` handlers. See [Using InitO with your
framework](frameworks.md) — with runnable examples for FastAPI, Django, Sanic,
aiohttp, Redis, boto3, and more.

## When to use InitO

Reach for InitO on the classes that are mostly **data** — DTOs, domain/value
objects, configuration, and service objects. It removes the mechanical methods
they need without changing what they are: after decoration they're still plain
Python classes you can subclass, pickle, and construct directly. It composes
with, rather than replaces, validation/ORM layers like Pydantic and SQLAlchemy.

```{toctree}
:hidden:

user-guide
reference/index
```
