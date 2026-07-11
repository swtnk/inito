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
    def __init__(self) -> None:
        self.rows = {1: "Ada"}


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

| Symbol | Role |
|---|---|
| `@Service` / `@Component` | register a class in a container (defaults to singleton scope) |
| `@Singleton` | sugar for `@Service(scope=Scope.SINGLETON)` |
| `@Inject` | wrap a function so its annotated parameters are filled from a container |
| `Container` | the registry + resolver; a shared `default_container` exists |
| `Scope` | `SINGLETON` (cached) or `TRANSIENT` (rebuilt each time) |

`@Component` is a literal alias for `@Service`; use whichever name you
prefer.

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
class Cache:
    def __init__(self, db: Database, ttl: int = 60) -> None:
        ...   # db is autowired; ttl keeps its default
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

## Errors

| Exception | When |
|---|---|
| `DependencyRegistrationError` | a constructor parameter has no type annotation, or a class is registered twice |
| `UnresolvableDependencyError` | a needed type is unregistered and has no default; or `get()` is called for an unregistered class |
| `CircularDependencyError` | the dependency graph has a cycle (`A → B → A`); the message lists the cycle |

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
