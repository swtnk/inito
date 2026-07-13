# InitO

[![PyPI version](https://img.shields.io/pypi/v/inito.svg)](https://pypi.org/project/inito/)
[![Python versions](https://img.shields.io/pypi/pyversions/inito.svg)](https://pypi.org/project/inito/)
[![License: MIT](https://img.shields.io/pypi/l/inito.svg)](https://github.com/swtnk/inito/blob/main/LICENSE)
[![CI](https://github.com/swtnk/inito/actions/workflows/ci.yml/badge.svg)](https://github.com/swtnk/inito/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-swetanksubham.com%2Finito-blue.svg)](https://swetanksubham.com/inito/)

**InitO is a zero-dependency Python library that eliminates data-class
boilerplate.** Decorate a class and InitO writes its constructor, `repr`,
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
and accessors. With InitO it's the three lines above — and the generated methods
are the *same* code you would have written, [benchmarked at
parity](#performance) with handwritten classes and `dataclasses`.

---

## Table of contents

- [Why InitO](#why-inito)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Decorators](#decorators)
  - [`@Data`](#data) · [`@Value`](#value) · [`@Getter` / `@Setter`](#getter--setter)
  - [`@ToString`](#tostring) · [`@EqualsAndHashCode`](#equalsandhashcode)
  - [Constructors](#constructors) · [`@Builder`](#builder) · [`@Config`](#config) · [`@Jsonize`](#jsonize)
  - [Composing decorators](#composing-decorators) · [Lowercase aliases](#lowercase-aliases)
- [Dependency injection](#dependency-injection)
  - [`@Service` / `@Singleton` / `@Inject`](#service--singleton--inject)
  - [Scopes](#scopes) · [Multiple implementations (qualifiers)](#multiple-implementations-qualifiers)
  - [Configuration injection](#configuration-injection) · [Factory (call-time arguments)](#factory-call-time-arguments)
  - [Resources (lifecycle and teardown)](#resources-lifecycle-and-teardown) · [Scopes and async](#scopes-and-async) · [FastAPI](#fastapi)
  - [Testing with overrides](#testing-with-overrides)
- [Type checking](#type-checking)
- [Using InitO with frameworks](#using-inito-with-frameworks)
- [Framework examples](#framework-examples) — [FastAPI](#fastapi) · [Django](#django) · [Sanic](#sanic) · [aiohttp](#aiohttp) · [Clients (boto3, Redis, …)](#clients-boto3-redis-)
- [Immutability](#immutability)
- [Self-referential fields](#self-referential-fields)
- [Performance](#performance)
- [How it works](#how-it-works)
- [Exceptions](#exceptions)
- [When to use InitO](#when-to-use-inito)
- [Compared to `dataclasses` / `attrs` / Pydantic](#compared-to-dataclasses--attrs--pydantic)
- [Documentation](#documentation) · [Contributing](#contributing) · [License](#license)

---

## Why InitO

- **Real methods, generated once.** InitO builds actual Python functions from
  your fields when the class is defined, compiles them with `exec()`, and
  attaches them — no `__getattr__`, proxies, descriptors, or runtime
  interception. At runtime your objects are ordinary instances, so construction,
  attribute access, `==`, and `hash()` run at handwritten speed.
- **Zero runtime dependencies.** InitO imports nothing outside the standard
  library. It installs cleanly into any project and any environment.
- **À la carte.** `@Data` is the all-in-one, but every capability is also a
  standalone decorator — take only the constructor, only the accessors, only the
  builder. You never pay for what you don't ask for.
- **Typed for both checkers.** A bundled [mypy plugin](#type-checking) makes
  `mypy --strict` see every generated member; [`inito-stubgen`](#type-checking)
  does the same for pyright / Pylance.
- **Batteries included.** Genuine immutability (`@Value`), fluent builders
  (`@Builder`), environment-backed configuration (`@Config`), and a small
  dependency-injection layer — all with the same generate-once, zero-dependency
  design.

## Installation

```bash
pip install inito       # or:  uv add inito
```

Requires **Python 3.9+** (tested through 3.14). No runtime dependencies.

Optional extras (dev-time only):

| Extra | Pulls in | For |
|---|---|---|
| `inito[stubgen]` | `mypy` | the `inito-stubgen` tool (pyright type stubs) |
| `inito[dev]` | test/lint/docs toolchain | contributing |

## Quick start

```python
from inito import Data, Value, builder, RequiredArgsConstructor, Service, Singleton, Inject

@Data                       # constructor + repr + eq + hash + get_x/set_x
class User:
    name: str
    age: int = 0

@Value                      # like @Data, but immutable and setter-free
class Point:
    x: int
    y: int

@builder                    # fluent Cls.builder().x(1).build()
class Request:
    url: str
    method: str = "GET"

@Singleton                  # DI: one shared instance per container
class Db:
    users = {1: "Ada"}      # seed data — no constructor needed

@Service                    # DI: autowired from the container on demand
@RequiredArgsConstructor    # inito writes __init__(self, db) — you don't
class Users:
    db: Db

@Inject                     # fills in `users` from the container
def main(users: Users) -> None:
    print(users.db.users[1])          # Ada

main()
```

## Decorators

Each decorator can be used bare (`@Data`) or with options (`@Data(frozen=True)`),
and reads fields from the class's **type annotations** (required fields first,
defaulted fields after — matching normal Python parameter ordering). Adding or
renaming a field automatically changes what gets generated the next time the
module is imported; there is nothing to keep in sync.

### `@Data`

The all-in-one. Generates a constructor, `__repr__`, `__eq__`, `__hash__`, and
`get_<field>()`/`set_<field>(value)` accessors for every field.

```python
@Data
class User:
    name: str
    age: int = 0
```

**Options** (`DataOptions`):

| Option | Default | Effect |
|---|---|---|
| `frozen` | `False` | genuinely immutable: no setters; assignment/deletion raise `FrozenInstanceError` |
| `include_getters` | `True` | generate `get_<field>()` |
| `include_setters` | `True` | generate `set_<field>(value)` |

```python
@Data(frozen=True)            # immutable
@Data(include_setters=False)  # read-only accessors, still mutable via `self.x = ...`
```

### `@Value`

Like `@Data` but **genuinely immutable** and setter-free — constructor,
`__repr__`, `__eq__`, `__hash__`, and getters, never setters. No
`@dataclass(frozen=True)` stacking needed.

```python
@Value
class Point:
    x: int
    y: int


p = Point(1, 2)
p.x = 5   # raises dataclasses.FrozenInstanceError
```

**Options** (`ValueOptions`): `include_getters` (default `True`).

### `@Getter` / `@Setter`

Just the accessors — `get_<field>()` and/or `set_<field>(value)` for every
field, nothing else.

```python
@AllArgsConstructor    # accessors add no constructor; bring your own
@Getter
@Setter
class Box:
    value: int


box = Box(1)
box.get_value()      # 1
box.set_value(2)
```

### `@ToString`

Just `__repr__`. Pairs well with `@Builder` for a readable repr without pulling
in `@Data`'s constructor/eq/hash.

```python
@ToString
class Point:
    x: int
    y: int
```

### `@EqualsAndHashCode`

Just `__eq__` and `__hash__` (always generated together). Equality is value-based
over all fields; instances of different classes compare unequal.

```python
@EqualsAndHashCode
class Money:
    amount: int
    currency: str
```

### Constructors

Three constructor-only decorators that generate an `__init__` and nothing else:

```python
@NoArgsConstructor          # def __init__(self): uses each field's default
class Config:
    retries: int = 3

@AllArgsConstructor         # def __init__(self, host, port): every field
class Address:
    host: str
    port: int

@RequiredArgsConstructor    # def __init__(self, host): only fields without a default
class Server:
    host: str
    port: int = 8080
```

`@NoArgsConstructor` requires every field to have a default (else
`InvalidFieldDefinitionError`). `@RequiredArgsConstructor` pairs naturally with
[dependency injection](#dependency-injection).

### `@Builder`

A fluent, chainable builder: `Cls.builder().field(value)...build()`. Works on a
plain class, or stacked on `@dataclass`/`@Data`.

```python
from dataclasses import dataclass
from inito import builder


@builder(to_builder=True)
@dataclass
class Request:
    prompt: str
    temperature: float = 0.7


request = Request.builder().prompt("hello").build()
revised = request.to_builder().temperature(0.9).build()   # copy-and-modify
```

**Options** (`BuilderOptions`):

| Option | Default | Effect |
|---|---|---|
| `to_builder` | `False` | also generate `instance.to_builder()` (pre-populated from `self`) |
| `setter_prefix` | `""` | prefix for fluent setters, e.g. `"with_"` → `.with_prompt(...)` |
| `build_method_name` | `"build"` | rename the terminal `build()` method |
| `use_init` | `False` | construct through the class's own `__init__` (runs framework/validating constructors — see [frameworks](#using-inito-with-frameworks)) |

By default `build()` assigns fields directly (fast, bypasses `__init__`); a
required field left unset raises `BuilderValidationError`.

### `@Config`

Load a class's fields from **environment variables**, coerced to the annotated
type, at construction — then autowire it by type via
[dependency injection](#configuration-injection). Zero dependencies (stdlib only).

```python
from inito import Config


@Config(prefix="APP_")
class Settings:
    database_url: str                 # required -> reads APP_DATABASE_URL
    port: int = 5432                  # optional -> APP_PORT, coerced to int
    debug: bool = False               # "1"/"true"/"yes"/"on" -> True


settings = Settings()                 # reads os.environ
```

Supports `str`/`int`/`float`/`bool`/`Optional[...]`. A required field with no env
value and no default raises `ConfigResolutionError`.

### `@Jsonize`

Generates `to_dict()` and `to_json()` that serialize every declared field, coercing
the types `json.dumps` chokes on — `datetime`/`date`/`time` (ISO 8601), `UUID`,
`Decimal`, `Enum`, `bytes` (base64), `Path`, mappings/sequences/sets, and nested
`@Jsonize` objects.

```python
import datetime, uuid
from inito import Data, Jsonize


@Jsonize
@Data
class Event:
    id: uuid.UUID
    when: datetime.datetime
    name: str = ""


event.to_dict()               # {"id": "…", "when": "2026-…T…", "name": "launch"}
event.to_json(sort_keys=True) # kwargs forwarded to json.dumps
```

Handy for APIs (return `obj.to_dict()` from a FastAPI handler), logging, and
storage. Both the mypy plugin and `inito-stubgen` expose `to_dict`/`to_json`.

### Composing decorators

`@Data` is exactly the composition of the atomic decorators — you can spell it
out to take only what you need:

```python
@AllArgsConstructor
@ToString
@EqualsAndHashCode
@Getter
@Setter
class User:              # functionally equivalent to @Data
    name: str
    age: int
```

Each atomic decorator resolves the *same* underlying generator `@Data` uses, so
there's no duplicated logic — only a more explicit spelling.

### Lowercase aliases

Every PascalCase decorator has a lowercase alias bound to the **same object** —
`data = Data`, `builder = Builder`, `value = Value`, `service = Service`, etc.
Use whichever reads better; `@builder` and `@Builder` are identical.

## Dependency injection

A small, lazy, thread-safe DI layer with the same zero-dependency,
annotation-native design — no XML, no `Provide[]` markers, no provider objects.
You annotate constructors; a `Container` wires them.

**A `Container` is a registry and a resolver in one.** It records which classes
are available for injection and what each one's constructor needs, then on demand
builds instances, wires their dependencies bottom-up, caches them by scope, and
hands them back. A shared `default_container` already exists, so you rarely
create one by hand.

| Concept | What it is |
|---|---|
| `@Service` / `@Component` | Marks a class as **available for injection** — registers it and the types its constructor needs. Never instantiates or mutates the class. |
| `@Singleton` | `@Service` with singleton lifetime (the default). |
| `@Inject` | Wraps a **function** so a container fills its annotated parameters the caller didn't supply. |
| `Container` | The **registry + resolver + lifetime manager**. `container.get(cls)` builds `cls` — wiring its dependencies — and returns it. |
| `default_container` | The shared `Container` that `@Service`/`@Singleton` use unless you pass `container=`. |
| `Scope` | A service's **lifetime**: `SINGLETON` (one cached instance), `TRANSIENT` (fresh every time), `THREAD_LOCAL` (one per thread). |
| `Qualifier` | Picks **which implementation** to inject when several share a base type. |
| `Factory[T]` | Inject a **callable** that builds a fresh `T` on demand — autowiring its registered deps, taking the rest as call-time arguments. |
| `@Resource` | Mark a class or generator whose instance the container **opens lazily and closes** (LIFO) at `shutdown_resources()` / `with container`. |
| `container.scope()` | Open a **scope** for `Scope.SCOPED` services — one instance per scope; scoped resources torn down at exit. |
| `Injected[T]` | A **FastAPI** dependency that resolves `T` from the container per request, inside a per-request scope. |

### `@Service` / `@Singleton` / `@Inject`

```python
from inito import Inject, RequiredArgsConstructor, Service, Singleton, default_container


@Singleton                       # one shared instance per container
class Database:
    users = {1: "Ada"}           # seed data — no constructor needed


@Service                         # registered; autowired from its constructor types
@RequiredArgsConstructor         # inito writes __init__(self, db) from the field
class UserService:
    db: Database

    def name(self, user_id: int) -> str:
        return self.db.users[user_id]


@Inject                          # fills annotated, unfilled params from the container
def handler(service: UserService) -> None:
    print(service.name(1))       # Ada


handler()
default_container.get(UserService).name(1)        # explicit resolution — same wiring
UserService(Database())                            # still an ordinary class
```

- **`@Service`** / **`@Component`** register a class's constructor dependency
  types into a `Container` **at decoration time** — it never instantiates
  anything and never mutates the class.
- **`@Singleton`** is sugar for `@Service(scope=Scope.SINGLETON)` (the default
  scope).
- **`@Inject`** wraps a function; on each call it resolves the annotated
  parameters the caller didn't supply. Safe on `async` handlers.
- **`Container.get(cls)`** resolves and builds the dependency graph lazily,
  bottom-up, on first request. `default_container` is used unless you pass
  `container=` to the decorators. Circular graphs raise `CircularDependencyError`
  with the full path; a missing dependency raises `UnresolvableDependencyError`.

Constructor params typed as a **registered** service are autowired; an
unregistered param with a **default** is left to that default; an unregistered
param with no default raises. So a class can mix real dependencies and plain
config: `def __init__(self, repo: Repo, retries: int = 3)`.

### Scopes

```python
from inito import Service, Scope

@Service(scope=Scope.SINGLETON)      # one instance per container (default)
@Service(scope=Scope.TRANSIENT)      # a fresh instance on every resolution
@Service(scope=Scope.THREAD_LOCAL)   # one instance per thread
class Worker: ...
```

Singleton construction is thread-safe (double-checked locking, per class); the
warm/cached `get()` path is lock-free.

### Multiple implementations (qualifiers)

When several classes implement one base type, select by name with
`typing.Annotated` — no markers:

```python
from typing import Annotated
from inito import Service, Qualifier


@Service(qualifier="postgres", primary=True)
class PostgresRepo(Repo): ...

@Service(qualifier="sqlite")
class SqliteRepo(Repo): ...


@Service
@RequiredArgsConstructor
class Users:
    repo: Annotated[Repo, Qualifier("postgres")]     # -> PostgresRepo


@Service
@RequiredArgsConstructor
class Reports:
    repo: Repo                                        # bare interface -> the `primary`
```

A bare interface with several implementations and no `primary` raises
`AmbiguousDependencyError` naming the candidates. A bare string
(`Annotated[Repo, "postgres"]`) works too.

### Configuration injection

A [`@Config`](#config) class (or a Pydantic `BaseSettings`) registered as a
`@Service` is autowired by type — 12-factor settings with no globals:

```python
@Service
@Config(prefix="APP_")
class Settings:
    database_url: str = "sqlite:///app.db"


@Service
@RequiredArgsConstructor
class App:
    settings: Settings                    # loaded from the environment, autowired
```

### Factory (call-time arguments)

A `@Service` is built once with *every* parameter autowired. When an object has to
be built **on demand from runtime data** — a report for a title, a session for a
request — inject a `Factory[T]` and call it:

```python
from inito import Factory, RequiredArgsConstructor, Service, Singleton


@Singleton
class Renderer:
    def render(self, title: str) -> str:
        return f"[{title}]"


class Report:
    def __init__(self, renderer: Renderer, title: str) -> None:   # renderer autowired, title supplied
        self.body = renderer.render(title)


@Service
@RequiredArgsConstructor
class Dashboard:
    make_report: Factory[Report]                # a callable that builds a Report

    def sales(self) -> str:
        return self.make_report(title="Sales").body     # -> "[Sales]"
```

`make_report(title="Sales")` builds a **fresh** `Report`: `renderer` is autowired,
`title` comes from the call. Call-time keyword arguments win; every other
registered-typed parameter is autowired; anything left falls to the target's own
default. The target need not itself be registered (it's a *prototype* factory), and
because a factory is lazy a `Factory[B]` parameter can **break a would-be cycle**.
`mypy` and pyright both infer `make_report(...) -> Report` with no plugin.

### Resources (lifecycle and teardown)

A singleton is opened once — but pools, clients, and sessions must also be
**closed**, in reverse order. `@Resource` marks something the container tears down
at `shutdown_resources()` or when a `with container:` block exits (resources are
still built lazily). Mark a class — torn down by its `close()` method (or the
`__enter__`/`__exit__` protocol) — or a generator function whose post-`yield` code
is the teardown:

```python
from collections.abc import Iterator

from inito import RequiredArgsConstructor, Resource, Service


@Service
@Resource
@RequiredArgsConstructor
class Database:
    dsn: str
    def close(self) -> None:                       # called at teardown
        self._pool.close()


@Resource
def cache(settings: Settings) -> Iterator[Cache]:  # settings autowired
    c = Cache(settings.url)
    yield c                                         # what container.get(Cache) returns
    c.disconnect()                                  # runs at shutdown


with container:
    db = container.get(Database)                    # opened on first get()
    ...
# db.close() (and every other resource) runs here, in reverse order
```

Rename the method with `@Resource(close="dispose")`. **Async** resources — a class
with an `async` `aclose()` or an `async def` generator — are torn down by
`await container.ashutdown_resources()` / `async with container`, and an async
generator provider is built with `await container.aget(Cls)`. Teardown is
best-effort: every resource is closed even if one raises, and failures are
aggregated into one `ResourceTeardownError`.

### Scopes and async

`Scope.SCOPED` gives **one instance per scope** — a request, a task, a unit of
work — resolved inside `with container.scope():` (or `async with`). A scoped
`@Resource` (e.g. a per-request DB session) is opened lazily and closed at scope
exit. `await container.aget(cls)` is the async twin of `get()`: it resolves the
**whole graph**, awaiting async `@Resource` providers anywhere in it.

```python
@Service(scope=Scope.SCOPED)
class UnitOfWork: ...


with container.scope():
    uow = container.get(UnitOfWork)          # one per scope; scoped resources closed on exit
```

### FastAPI

`Injected[T]` resolves a service from the container per request, inside a
per-request scope (so scoped resources open and close automatically). FastAPI is
optional — inito never imports it at runtime.

```python
from inito import Injected


@app.get("/users/{user_id}")
async def read_user(user_id: int, service: Injected[UserService]) -> dict:
    return service.get(user_id)
```

### Testing with overrides

Swap any dependency for a fake — no monkeypatching:

```python
container.override(Repo, FakeRepo())               # fixed instance
container.override_factory(Repo, lambda: FakeRepo())  # fresh each resolution

with container.overrides({Repo: FakeRepo()}):      # scoped; restored on exit
    ...

container.clear_overrides()
```

Overrides win over the singleton cache and don't require the type to be
registered. `container.reset()` clears the instance caches and overrides (not
registrations).

## Type checking

Because InitO attaches members at decoration time, type-checkers need a little
help to see them — and InitO ships that help for both major checkers:

**mypy** — enable the bundled plugin; `mypy --strict` then sees every generated
member (the real `__init__` signature, `get_x`/`set_x`, the `@Builder` chain):

```toml
[tool.mypy]
plugins = ["inito.typing.mypy_plugin"]
```

**pyright / Pylance** — pyright has no plugin mechanism, so generate stub files
with the bundled tool; pyright then reads the sibling `.pyi` and sees every
generated member:

```bash
pip install "inito[stubgen]"
inito-stubgen src/          # writes a .pyi next to each module with inito classes
```

`@Data`/`@Value`/`@AllArgsConstructor` constructors are already typed under
pyright natively (via `typing.dataclass_transform`, PEP 681); `inito-stubgen`
adds accessors, the `@Builder` chain, and the other constructors. Re-run it when
your decorated classes change, or wire it into pre-commit.

## Using InitO with frameworks

InitO has zero dependencies and generates plain methods on plain classes, so it
drops into any project — FastAPI, Django, Sanic, aiohttp, Flask, or none. It
**composes with** your stack rather than replacing it; it is not an ORM or a
validation layer.

- On a framework **model** (Pydantic, SQLAlchemy, Django), let the framework own
  construction and use the **additive** decorators
  (`@Getter`/`@Setter`/`@ToString`/`@EqualsAndHashCode`).
- **Pydantic v2 is auto-detected:** bare `@Builder` on a `BaseModel` constructs
  through Pydantic's validating `__init__` and reads defaults from the model, so
  it "just works"; the constructor-generating decorators (`@Data`, `@Value`, …)
  refuse to run on a Pydantic model (they'd overwrite validation) with a clear
  error.
- For **SQLAlchemy** / **Django** / any hand-written constructor, use
  `@Builder(use_init=True)` to build through the real constructor.
- The DI layer is safe to resolve from `async` request handlers.

## Framework examples

Define your services once, then wire the same container into any framework. The
snippets below all reuse this block:

```python
# services.py — shared by every example below
from inito import Container, RequiredArgsConstructor, Service, Singleton

container = Container()


@Singleton(container=container)          # one shared instance per container
class UserRepo:
    _NAMES = {1: "Ada", 2: "Linus"}      # seed data — no constructor needed

    def name(self, user_id: int) -> str | None:
        return self._NAMES.get(user_id)


@Service(container=container)            # autowired from its constructor types
@RequiredArgsConstructor                 # inito writes __init__(self, repo) — you don't
class Greeter:
    repo: UserRepo

    def greet(self, user_id: int) -> str:
        return f"Hello, {self.repo.name(user_id) or 'stranger'}!"
```

> **Dogfooding note:** the services declare their dependencies as fields and let
> InitO write the constructor (`@RequiredArgsConstructor`) — the same
> boilerplate this library removes. A hand-written `__init__` remains only where
> it does real work (building an external client below), not mere field
> forwarding.

### FastAPI

A tiny `provide()` helper turns any registered service into a `Depends`, so
routes stay ordinary FastAPI functions:

```python
from fastapi import Depends, FastAPI
from services import Greeter, container

app = FastAPI()


def provide(service_type):
    return Depends(lambda: container.get(service_type))


@app.get("/greet/{user_id}")
def greet(user_id: int, greeter: Greeter = provide(Greeter)):
    return {"message": greeter.greet(user_id)}
```

### Django

A view pulls the service from the container and returns a response:

```python
from django.http import JsonResponse
from django.urls import path
from services import Greeter, container


def greet(request, user_id: int):
    return JsonResponse({"message": container.get(Greeter).greet(user_id)})


urlpatterns = [path("greet/<int:user_id>", greet)]
```

### Sanic

```python
from sanic import Sanic, json
from services import Greeter, container

app = Sanic("example")


@app.get("/greet/<user_id:int>")
async def greet(request, user_id: int):
    return json({"message": container.get(Greeter).greet(user_id)})
```

### aiohttp

```python
from aiohttp import web
from services import Greeter, container


async def greet(request: web.Request) -> web.Response:
    user_id = int(request.match_info["user_id"])
    return web.json_response({"message": container.get(Greeter).greet(user_id)})


app = web.Application()
app.router.add_get("/greet/{user_id}", greet)
```

### Clients (boto3, Redis, …)

Wire an external client as a `@Singleton` built from `@Config` settings, then
inject it by type. The same shape works for boto3, Redis, Valkey, RabbitMQ, a
database pool — anything:

```python
import boto3
from inito import Config, Container, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="AWS_")
class AwsSettings:
    region: str = "us-east-1"          # reads AWS_REGION


@Singleton(container=container)
class S3Client:
    def __init__(self, settings: AwsSettings) -> None:   # builds the client — real work
        self.client = boto3.client("s3", region_name=settings.region)


@Service(container=container)
@RequiredArgsConstructor                                 # inito writes the constructor
class Storage:
    s3: S3Client

    def bucket_names(self) -> list[str]:
        return [b["Name"] for b in self.s3.client.list_buckets()["Buckets"]]


storage = container.get(Storage)         # S3Client built once, injected
```

```python
# Redis is the same shape — swap the client and the @Config prefix:
import redis


@Singleton(container=container)
class Cache:
    def __init__(self, settings: RedisSettings) -> None:
        self.client = redis.Redis.from_url(settings.url)
```

**In tests**, swap any real client for a fake with no monkeypatching:

```python
container.override(S3Client, FakeS3Client())   # get(Storage) now uses the fake
```

Full, runnable, override-tested versions of all of these — plus RabbitMQ, Valkey,
and env-config — live in
[`examples/di/`](https://github.com/swtnk/inito/tree/main/examples/di). Interop
is verified in CI against Pydantic v2, SQLAlchemy 2.0, and Django on Python
3.9–3.14. See also [Using InitO with your
framework](https://swetanksubham.com/inito/frameworks.html).

## Immutability

`@Value` and `@Data(frozen=True)` are genuinely immutable on their own — no
`@dataclass(frozen=True)` stacking needed. Attribute assignment and deletion
always raise `dataclasses.FrozenInstanceError` after construction:

```python
@Value
class Point:
    x: int
    y: int


point = Point(1, 2)
point.x = 5   # raises FrozenInstanceError
del point.x   # also raises
```

Internally, an immutable class's constructor (and `@Builder`'s `build()`) assigns
fields via `object.__setattr__` — the same technique a real frozen dataclass's
`__init__` uses — so construction always succeeds while post-construction
mutation is blocked. A non-frozen class uses a plain `self.x = x`, which is both
faster and keeps attribute reads at handwritten speed.

To stack a decorator with `@dataclass(frozen=True)`, put the
`@dataclass(frozen=True)` **innermost** (closest to the class) so InitO sees the
frozen `__setattr__` when it generates the constructor. The reverse order is not
supported — prefer `@Value` / `@Data(frozen=True)`.

## Self-referential fields

Self-referential type hints work — resolved once, at decoration time:

```python
from typing import Optional
from inito import Data


@Data
class Node:
    value: int
    next: Optional[Node] = None
```

Use `Optional[Node]` rather than `Node | None` for such a field: the annotation
is evaluated at runtime, and `|` union syntax isn't valid there before Python
3.10 (InitO supports 3.9+).

## Performance

Because InitO generates real methods and gets out of the way, its objects are at
**parity with handwritten classes and `dataclasses`** — construction, attribute
access, `==`, `hash()`, and `repr()`. There is no per-instance or per-call InitO
overhead; the only cost is a one-time, decoration-time code generation when the
class is first defined.

The dependency-injection layer adds a small, quantified (not hidden) cost only on
the cold path (building a graph the first time); a warm singleton `get()` is a
single dict lookup, and attribute access on a resolved instance is at parity. See
the [performance page](https://swetanksubham.com/inito/performance.html) for the
measured numbers vs. handwritten, `dataclasses`, and `attrs`.

## How it works

InitO follows one strict rule: **all reflection happens exactly once, at
decoration time.** Each decorator reads the class's annotations, builds the
source text of a real Python function, compiles it with `exec()`, and attaches
the resulting function object to the class — just as if you had typed it. At
runtime there is no InitO left in the picture: no `__getattr__`, no proxies, no
descriptors, no monkeypatching. That is why the generated methods run at
handwritten speed, and why the whole library needs zero runtime dependencies.

## Exceptions

All errors inherit from `inito.exceptions.InitoError`:

| Exception | Raised when |
|---|---|
| `DecoratorConfigurationError` | a decorator is misused (bad argument; applied to a Pydantic model) |
| `InvalidFieldDefinitionError` | e.g. `@NoArgsConstructor` on a field without a default |
| `AnnotationResolutionError` | a field annotation can't be resolved |
| `BuilderValidationError` | `build()` called with a required field unset |
| `ConfigResolutionError` | a `@Config` field has no env value and no default |
| `DependencyRegistrationError` | duplicate registration / unannotated constructor param |
| `UnresolvableDependencyError` | a needed dependency isn't registered and has no default |
| `CircularDependencyError` | a dependency graph revisits a class mid-resolution |
| `AmbiguousDependencyError` | several implementations of a type and no `primary` |
| `CodeGenerationError`, `MetadataExtractionError`, `DuplicateGeneratorError` | internal generation/registry errors |

## When to use InitO

Reach for InitO on the classes that are mostly **data**: DTOs, domain/value
objects, configuration, and service objects. It removes the mechanical methods
those classes need without changing what they are — after decoration they're
still plain Python classes you can subclass, pickle, and construct directly.

Don't use it as an ORM or a validation layer; compose it with Pydantic /
SQLAlchemy / Django for those (see [frameworks](#using-inito-with-frameworks)).

## Compared to `dataclasses` / `attrs` / Pydantic

- **`dataclasses`** — InitO composes *with* it and adds what it doesn't have:
  `get_x`/`set_x` accessors, a fluent builder, and à-la-carte decorators (take
  only the pieces you need). Both are zero-dependency and at the same speed.
- **`attrs`** — one flexible entry point vs. InitO's many small, explicit
  decorators; `attrs` has the more mature IDE story today, while InitO ships a
  mypy plugin *and* `inito-stubgen` for pyright, with zero runtime dependencies.
- **Pydantic** — a validation/serialization framework, a different job. Use
  Pydantic for I/O boundaries and InitO for plain domain/service objects; they
  [interoperate](#using-inito-with-frameworks).

See the [migration guide](https://swetanksubham.com/inito/migration.html) for a
side-by-side.

## Documentation

Full documentation — a page per decorator, the dependency-injection guide,
framework guides, recipes, performance, and the API reference — is at
**[swetanksubham.com/inito](https://swetanksubham.com/inito/)**.

## Contributing

See [CONTRIBUTING.md](https://github.com/swtnk/inito/blob/main/CONTRIBUTING.md).

## License

MIT — see [LICENSE](https://github.com/swtnk/inito/blob/main/LICENSE).
