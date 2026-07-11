# inito

[![PyPI version](https://img.shields.io/pypi/v/inito.svg)](https://pypi.org/project/inito/)
[![Python versions](https://img.shields.io/pypi/pyversions/inito.svg)](https://pypi.org/project/inito/)
[![License: MIT](https://img.shields.io/pypi/l/inito.svg)](https://github.com/swtnk/inito/blob/main/LICENSE)
[![CI](https://github.com/swtnk/inito/actions/workflows/ci.yml/badge.svg)](https://github.com/swtnk/inito/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-swetanksubham.com%2Finito-blue.svg)](https://swetanksubham.com/inito/)

**inito is a zero-dependency Python library that eliminates data-class
boilerplate.** Decorate a class and inito writes its constructor, `repr`,
equality, hashing, accessors, and builder for you — as *real methods*, generated
once when the class is defined, running as fast as code you'd write by hand.

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

By hand, `User` is ~20 lines of `__init__`, `__repr__`, `__eq__`, `__hash__`,
and accessors. With inito it's the three lines above — and the generated methods
are the *same* code you would have written, [benchmarked at
parity](https://swetanksubham.com/inito/performance.html) with handwritten
classes and `dataclasses`.

## Why inito

- **Real methods, generated once.** inito builds actual Python functions from
  your fields when the class is defined, then attaches them — no `__getattr__`,
  proxies, descriptors, or runtime interception. At runtime your objects are
  ordinary instances, so construction, attribute access, `==`, and `hash()` run
  at handwritten speed.
- **Zero runtime dependencies.** inito imports nothing outside the standard
  library, so it installs cleanly into any project and any environment.
- **À la carte.** `@Data` is the all-in-one, but every capability is also a
  standalone decorator — take only the constructor, only the accessors, only the
  builder. You never pay for what you don't ask for.
- **Typed.** A bundled [mypy plugin](#type-checking) makes `mypy --strict` see
  every generated member; [`inito-stubgen`](#type-checking) does the same for
  pyright / Pylance.
- **Batteries included.** Genuine immutability (`@Value`), fluent builders
  (`@Builder`), and a small dependency-injection layer
  (`@Service`/`@Singleton`/`@Inject`) — all with the same zero-dependency,
  generate-once design.

## Install

```bash
pip install inito       # or:  uv add inito
```

Requires Python 3.9+ (tested through 3.14). No other dependencies.

## Quick start

**`@Data` — the all-in-one.** Constructor, `repr`, equality, hashing, and
`get_x`/`set_x` accessors for every field:

```python
from inito import Data


@Data
class User:
    name: str
    age: int = 0


@Data(frozen=True)   # genuinely immutable: no setters; assignment/deletion raise
class Point:
    x: int
    y: int
```

**`@Builder` — a fluent, chainable builder** (composes with `@dataclass`):

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

**Dependency injection** — register a class, and a `Container` autowires its
constructor from other registered services:

```python
from inito import Inject, Service, Singleton


@Singleton                       # one shared instance per container
class Database:
    def __init__(self) -> None:
        self.users = {1: "Ada"}


@Service                         # autowired from the container on demand
class UserService:
    def __init__(self, db: Database) -> None:
        self.db = db


@Inject                          # fills in `service` from the container
def main(service: UserService) -> None:
    print(service.db.users[1])   # Ada


main()
```

`@Service` never rewrites your class — `UserService(Database())` still works like
any ordinary class; `container.get(UserService)` is the DI-aware path.

## What inito gives you

| Decorator | Generates |
|---|---|
| `@Data` | constructor · `__repr__` · `__eq__` · `__hash__` · `get_x`/`set_x` — the all-in-one |
| `@Value` | like `@Data` but **immutable** and setter-free |
| `@Getter` / `@Setter` | `get_x()` / `set_x(value)` accessors only |
| `@ToString` | `__repr__` only |
| `@EqualsAndHashCode` | `__eq__` + `__hash__` only |
| `@NoArgsConstructor` | zero-argument constructor using each field's default |
| `@AllArgsConstructor` | constructor taking every field |
| `@RequiredArgsConstructor` | constructor taking only fields without a default |
| `@Builder` / `builder` | fluent `Cls.builder().x(1).build()`, optional `.to_builder()` |
| `@Config` | load fields from environment variables, autowired by type |
| `@Service` / `@Singleton` / `@Inject` | dependency injection via a `Container` |

Every PascalCase decorator has a lowercase alias (`data`, `builder`, `value`, …)
bound to the same object — use whichever reads better.

## When to use inito

Reach for inito on the classes that are mostly **data**: DTOs, domain/value
objects, configuration, and service objects. It removes the mechanical methods
those classes need without changing what they are — after decoration they're
still plain Python classes you can subclass, pickle, and construct directly.

inito **composes with** your stack rather than replacing it. It is *not* an ORM
or a validation layer: on a Pydantic / SQLAlchemy / Django **model**, let the
framework own construction and use inito's additive decorators
(`@Getter`/`@Setter`/`@ToString`/`@EqualsAndHashCode`), or `@Builder(use_init=True)`
to build through the model's own validating constructor. See
[Using inito with your framework](https://swetanksubham.com/inito/frameworks.html).

## Type checking

Because inito attaches members at decoration time, type-checkers need a little
help to see them — and inito ships that help for both major checkers:

- **mypy** — enable the bundled plugin; `mypy --strict` then sees every
  generated member (the real `__init__` signature, `get_x`/`set_x`, the
  `@Builder` chain):

  ```toml
  [tool.mypy]
  plugins = ["inito.typing.mypy_plugin"]
  ```

- **pyright / Pylance** — pyright has no plugin mechanism, so generate stub
  files with the bundled tool; pyright then sees every generated member:

  ```bash
  pip install "inito[stubgen]"
  inito-stubgen src/          # writes a .pyi next to each module with inito classes
  ```

  `@Data`/`@Value`/`@AllArgsConstructor` constructors are already typed under
  pyright natively (via `dataclass_transform`); `inito-stubgen` adds the rest.

## Documentation

Full documentation — a page per decorator, dependency injection, framework
guides, recipes, and the API reference — is at
**[swetanksubham.com/inito](https://swetanksubham.com/inito/)**. A few things
worth knowing up front:

- **Immutability is genuine.** `@Value` and `@Data(frozen=True)` block attribute
  assignment and deletion (`FrozenInstanceError`) on their own — no
  `@dataclass(frozen=True)` stacking needed.
- **Self-referential fields work** (`next: Optional[Node]`), resolved once at
  decoration time.
- **Runs everywhere.** Zero dependencies, Python 3.9–3.14, interoperability
  verified in CI against Pydantic v2, SQLAlchemy 2.0, and Django.

See [runnable framework examples](examples/di/) (FastAPI, Django, Sanic, aiohttp,
Redis, Valkey, boto3, RabbitMQ) and the
[migration guide](https://swetanksubham.com/inito/migration.html) from
`dataclasses` / `attrs` / Pydantic.

## Contributing

See [CONTRIBUTING.md](https://github.com/swtnk/inito/blob/main/CONTRIBUTING.md).

## License

MIT — see [LICENSE](https://github.com/swtnk/inito/blob/main/LICENSE).
