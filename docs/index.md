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


# @Data wrote __init__, __repr__, __eq__, __hash__, get_name/set_name, ...
user = User("Ada", age=30)
print(user)              # User(name='Ada', age=30)
print(user.get_name())   # Ada
```

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`rocket;1.5em;sd-mr-1` Get started
:link: quickstart
:link-type: doc

Install InitO and tour every decorator in a few minutes.
:::

:::{grid-item-card} {octicon}`book;1.5em;sd-mr-1` User Guide
:link: user-guide
:link-type: doc

Task-oriented docs: a dedicated page per decorator, plus DI, recipes, and
migration.
:::

:::{grid-item-card} {octicon}`code-square;1.5em;sd-mr-1` API reference
:link: reference/index
:link-type: doc

Every decorator, option, and exception, generated from the source.
:::

:::{grid-item-card} {octicon}`light-bulb;1.5em;sd-mr-1` Concepts
:link: concepts
:link-type: doc

The boilerplate problem InitO solves — and how it stays fast.
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

::::

## Why InitO

- **Real methods, generated once.** Each decorator builds true Python
  functions from source at decoration time and attaches them to the class —
  no `__getattr__`, proxies, or descriptors. At runtime your objects are
  ordinary instances, so construction, attribute access, `==`, and `hash()`
  run at [handwritten speed](performance.md).
- **Pick exactly what you need.** `@Data` is the all-in-one, but every
  capability is also a standalone decorator (`@Getter`, `@ToString`,
  `@EqualsAndHashCode`, ...) — you never pay for what you don't ask for.
- **Composes with the standard library.** Stack any decorator with
  `@dataclass`; `@Builder` and the accessors work on plain classes too.
- **Typed for both checkers.** A bundled [mypy
  plugin](installation.md#type-checking-mypy) makes `mypy --strict` see every
  generated member, and [`inito-stubgen`](installation.md) does the same for
  pyright / Pylance.
- **Batteries for services.** A small
  [dependency-injection](dependency-injection.md) layer
  (`@Service`/`@Singleton`/`@Inject` + a `Container`) wires constructors
  together lazily and thread-safely.

## Decorators at a glance

| Decorator | Generates |
|---|---|
| `@Data` | constructor, `__repr__`, `__eq__`, `__hash__`, `get_x`/`set_x` — the all-in-one |
| `@Value` | like `@Data` but **immutable** and setter-free |
| `@Getter` / `@Setter` | `get_x()` / `set_x(value)` accessors only |
| `@ToString` | `__repr__` only |
| `@EqualsAndHashCode` | `__eq__` + `__hash__` only |
| `@NoArgsConstructor` | zero-argument constructor using each field's default |
| `@AllArgsConstructor` | constructor taking every field |
| `@RequiredArgsConstructor` | constructor taking only fields without a default |
| `@Builder` / `builder` | fluent `Cls.builder().x(1).build()`, optional `.to_builder()` |
| `@Service` / `@Singleton` / `@Inject` | dependency injection via a `Container` |

Every PascalCase decorator has a lowercase alias (`data`, `builder`, ...)
bound to the same object.

```{toctree}
:hidden:

user-guide
reference/index
```
