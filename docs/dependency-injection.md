# Dependency injection

A small, zero-dependency DI layer: `@Service`/`@Singleton` register classes,
`@Inject` autowires functions, and a `Container` resolves the graph lazily.

## The problem it solves

As an application grows, wiring objects together by hand becomes its own
chore: a handler needs a service, which needs a repository, which needs a
database connection — and every call site has to build that whole chain in
the right order. inito splits that into two jobs: the
[constructor decorators](decorators/constructors.md) declare what
a class depends on (its typed constructor parameters), and a `Container`
resolves and builds the graph for you, once, on demand.

Crucially, `@Service` **never rewrites your class** — it stays an ordinary,
directly-constructible Python class. The container is an *opt-in* way to
build it, not a replacement for `MyService(...)`.

## Quick example

```python
from inito import Service, Singleton, Inject, RequiredArgsConstructor, default_container


@Singleton                       # one shared instance per container
class Database:
    rows = {1: "Ada"}            # seed data — no constructor needed


@Service                         # autowired from the container on demand
@RequiredArgsConstructor
class UserRepository:
    db: Database                 # a field annotation is all it takes

    def name(self, user_id: int) -> str:
        return self.db.rows[user_id]


@Inject                          # fills `repo` from the container
def handler(repo: UserRepository) -> str:
    return repo.name(1)


print(handler())                             # Ada
print(default_container.get(UserRepository)) # explicit resolution, same wiring
plain = UserRepository(Database())           # still an ordinary class
```

## The pieces

**A `Container` is the heart of the system — a registry and a resolver in one.**
It holds *registrations* (which classes are available for injection and what
each one's constructor depends on), and on demand it builds instances, wires
their dependencies, caches them according to their scope, and hands them back.
You rarely create one by hand: a shared `default_container` already exists, and
`@Service`/`@Singleton` register into it. Make your own `Container` only to
isolate a subsystem's wiring or a test.

| Symbol | What it is |
|---|---|
| `@Service` / `@Component` | Marks a class as **available for injection** — registers it (and the types its constructor needs) in a container, at decoration time. It never instantiates or mutates the class; `MyService(...)` still works normally. |
| `@Singleton` | `@Service` with singleton lifetime (the default) — sugar for `@Service(scope=Scope.SINGLETON)`. |
| `@Inject` | Wraps a **function** so a container fills its type-annotated parameters that the caller didn't supply. |
| `Container` | The registry + resolver + lifetime manager. `container.get(cls)` builds `cls`, wiring its dependencies bottom-up, and returns it. |
| `default_container` | The shared `Container` that `@Service`/`@Singleton` use unless you pass `container=`. |
| `Scope` | A service's lifetime: `SINGLETON` (one cached instance), `TRANSIENT` (a fresh instance every time), or `THREAD_LOCAL` (one instance per thread). |
| `Qualifier` | Names *which* implementation to inject when several implement one base type — `Annotated[Repo, Qualifier("postgres")]`. |

`@Component` is a literal alias for `@Service`; use whichever name you prefer.

## How resolution works

`@Service` reads a class's constructor parameter types **once, at
decoration time**, and records them. Nothing is instantiated yet. The first
time you ask for the class — via `container.get(cls)` or an
`@Inject`-decorated call — the container resolves the dependency graph
bottom-up, builds each instance, and (for singletons) caches it.

A constructor parameter is **autowired only if its annotated type is itself
a registered service**. A parameter whose type is *not* registered:

- keeps its **default value** if it has one (plain config like
  `retries: int = 3` just works), or
- raises `UnresolvableDependencyError` if it has no default (the container
  has nothing to supply and no fallback).

```python
@Service
@AllArgsConstructor           # inito writes __init__(self, db, ttl=60)
class Cache:
    db: Database              # registered -> autowired
    ttl: int = 60             # not registered, has a default -> keeps 60
```

## Scopes

```python
from inito import Service, Scope
```

- **`Scope.SINGLETON`** (the default, and what `@Singleton` selects) builds
  the instance once and caches it — every `get()` after the first returns
  the same object.
- **`Scope.TRANSIENT`** never caches — every `get()` rebuilds the subtree:

  ```python
  @Service(scope=Scope.TRANSIENT)
  class RequestContext:
      def __init__(self) -> None:
          self.token = object()
  ```

- **`Scope.THREAD_LOCAL`** caches **one instance per thread** — every thread
  that resolves the service gets its own, shared within that thread. Useful for
  objects that aren't safe to share across threads (a connection, a cursor):

  ```python
  @Service(scope=Scope.THREAD_LOCAL)
  class Session:
      ...
  ```

One subtlety: a transient service used as a dependency of a *singleton* is
built once — at the singleton's first resolution — because the singleton
that holds it is itself cached. "Transient" means "fresh each time it is
resolved directly", not "fresh inside every consumer".

`@Singleton` is a standalone decorator, not something you stack on
`@Service`. Passing it a conflicting `scope=` argument raises
`DecoratorConfigurationError` — use `@Service(scope=...)` when you want a
non-default scope.

## Containers

`@Service`/`@Singleton` register into the shared `default_container` unless
you pass `container=`. Create your own `Container` to isolate a subsystem's
registrations — especially handy in tests:

```python
from inito import Service
from inito.di import Container

container = Container()


@Service(container=container)
class Repo:
    ...


container.get(Repo)             # resolved from the isolated container
container.is_registered(Repo)   # True
container.reset()               # clear cached singletons (keeps registrations)
```

`container.get(cls)` is typed generically (`type[T] -> T`), so both mypy and
pyright infer the returned type with no plugin or stub needed.

## Multiple implementations (qualifiers)

When several classes implement one base type, a bare `repo: Repo` parameter is
ambiguous. Name the one you want with `typing.Annotated` and a `Qualifier` — no
markers, no string keys scattered around:

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
    repo: Repo                                        # bare interface -> the `primary` one
```

- `@Service(qualifier="name")` registers an implementation under that name;
  `Annotated[Repo, Qualifier("name")]` (or a bare string, `Annotated[Repo,
  "name"]`) resolves it.
- A **bare** interface parameter resolves the sole registered implementation, or
  the one marked `@Service(primary=True)` when several exist. Several with no
  `primary` raises `AmbiguousDependencyError` naming the candidates.
- The qualifier is read once, at registration — never per `get()`.

## Configuration injection

A [`@Config`](decorators/config.md) class loads its fields from environment
variables; registered as a `@Service`, it is autowired by type like any other
dependency — 12-factor configuration with no globals or import-time reads:

```python
from inito import Config, RequiredArgsConstructor, Service


@Service
@Config(prefix="APP_")
class Settings:
    database_url: str = "sqlite:///app.db"     # reads APP_DATABASE_URL
    pool_size: int = 5                          # reads APP_POOL_SIZE, coerced to int


@Service
@RequiredArgsConstructor
class Database:
    settings: Settings                          # loaded from the environment, autowired

    def dsn(self) -> str:
        return self.settings.database_url
```

A Pydantic `BaseSettings` works the same way (it loads the environment itself) —
register it as a `@Service` and it autowires by type.

## Testing with overrides

Swap any dependency for a fake, with no monkeypatching, so a service under test
gets a stub instead of the real thing:

```python
container.override(Repo, FakeRepo())                  # a fixed instance
container.override_factory(Repo, lambda: FakeRepo())  # a fresh one each resolution

with container.overrides({Repo: FakeRepo()}):         # scoped; auto-restored on exit
    assert container.get(Users).repo.__class__ is FakeRepo

container.clear_override(Repo)                         # or clear_overrides() for all
```

An override wins over everything — including a cached singleton — and doesn't
require the type to be registered, so you can stub a collaborator the container
has never seen. `container.reset()` clears the instance caches **and** overrides
(registrations stay).

## Errors

| Exception | When |
|---|---|
| `DependencyRegistrationError` | a constructor parameter has no type annotation, or a class is registered twice |
| `UnresolvableDependencyError` | a needed type is unregistered and has no default; or `get()` is called for an unregistered class |
| `CircularDependencyError` | the dependency graph has a cycle (`A → B → A`); the message lists the cycle |
| `AmbiguousDependencyError` | a bare interface has several registered implementations and no `primary` |

## Performance and safety

- **Warm path is cheap.** Once a singleton is cached, `container.get(cls)` is
  a single dict lookup; using the resolved object afterward is ordinary
  Python with no DI overhead. See [Performance](performance.md).
- **`@Inject` has a real per-call cost** — it is the one decorator that does
  work on every call, since it fills a function's parameters from the
  container each time it is invoked (signature inspection is still done once,
  at decoration time). It targets composition-root entry points (a `main()`
  or request handler), not hot-path methods.
- **Thread-safe.** Concurrent first-access to a singleton constructs it
  exactly once (double-checked locking, per registered class); dependencies
  are resolved before the lock is taken, so cyclic graphs raise cleanly
  instead of deadlocking.
- **Process-local.** A `Container` lives in one process — like any in-memory
  Python object, its singletons are not shared across `multiprocessing`
  workers. Share cross-process state through a database, file, or shared
  memory instead.

## See also

- [Constructors](decorators/constructors.md) — `@RequiredArgsConstructor`
  pairs naturally with `@Service`.
- [Recipes](recipes.md) — a full service-layer example.
- [Troubleshooting](troubleshooting.md) — DI error walkthroughs.
- [API reference](reference/index.md)
