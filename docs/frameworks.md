# Using InitO with your framework

InitO has zero runtime dependencies and generates plain methods on plain
classes, so it drops into any Python project — Django, FastAPI, Sanic, Flask,
Litestar, or no framework at all. This page covers the two things worth knowing
when you combine it with a framework: which decorators to reach for on
framework model classes, and how the dependency-injection layer behaves in
async request handlers.

## The one rule: constructors vs. additive decorators

InitO's decorators fall into two groups:

- **Additive** — `@Getter`, `@Setter`, `@ToString`, `@EqualsAndHashCode`. These
  only *add* methods and never touch construction. They compose freely with any
  class, including framework models.
- **Constructor-owning** — `@Data`, `@Value`, `@NoArgsConstructor`,
  `@AllArgsConstructor`, `@RequiredArgsConstructor`, and `@Builder`'s default
  `build()`. These generate (or bypass) `__init__`.

Frameworks like **Pydantic**, **SQLAlchemy**, and **Django** run important logic
in their own `__init__` (validation, ORM instrumentation, field descriptors). So
on a framework's *model* class, prefer the additive decorators, and let the
framework own construction.

```python
from inito import Getter, ToString
from pydantic import BaseModel


@Getter
@ToString
class Settings(BaseModel):
    host: str = "localhost"
    port: int = 5432


s = Settings()
s.get_host()   # "localhost"  — inito accessor
repr(s)         # "Settings(host='localhost', port=5432)"  — inito __repr__
```

For your own **domain / DTO / service** objects — the classes that aren't a
framework base class — use the full set (`@Data`, `@Value`, `@Builder`) exactly
as you would anywhere.

## Builders that respect a framework constructor: `use_init=True`

By default `@Builder`'s `build()` assigns fields directly and **bypasses
`__init__`** — this is what keeps it fast and lets it work with InitO's own
immutable classes. On a validating model that means the framework's validation
would be skipped. Pass **`use_init=True`** and `build()` instead constructs
through the class's own `__init__`, so the framework's validation and
instrumentation run:

```python
from inito import Builder
from pydantic import BaseModel


@Builder(use_init=True)
class User(BaseModel):
    name: str
    age: int = 0        # Pydantic default (InitO can't see it)


User.builder().name("Ada").build()          # age -> Pydantic's default (0)
User.builder().name("Ada").age("nope").build()   # raises pydantic.ValidationError
```

In `use_init=True` mode the builder is a keyword-argument accumulator: only the
fields you actually set are passed to the constructor, so the *constructor's*
own defaults and required-argument errors apply — not InitO's. It works the
same way with SQLAlchemy 2.0 declarative models and any hand-written `__init__`:

```python
from inito import Builder
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


@Builder(use_init=True)
class Widget(Base):
    __tablename__ = "widget"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


widget = Widget.builder().id(1).name("gadget").build()   # fully instrumented ORM object
```

## Dependency injection in async handlers (FastAPI / Sanic / Starlette)

The DI container is safe to resolve from `async` code. `container.get()` and
`@Inject` are synchronous, do no I/O, and singleton construction is guarded by
double-checked locking, so concurrent resolution from many coroutines yields a
single shared instance with no deadlock.

`@Inject` wraps an `async def` transparently — it fills the container-known
parameters and returns the coroutine unchanged:

```python
from inito import Inject, Service, Singleton


@Singleton
class Repository:
    def __init__(self) -> None:
        self.users = {"ada": 30}


@Service
class UserService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo


# FastAPI example — the handler's dependencies are wired by InitO, not the route.
@Inject
async def get_age(name: str, service: UserService) -> int:
    return service.repo.users[name]
```

Register services at **module import time** (the decorator does this for you).
Because DI resolves constructor type hints at import, define your services at
module scope — a service class defined inside a function can't have its
annotations resolved against the module globals.

For a heavier request-scoped lifecycle, keep using your framework's own
dependency system (FastAPI `Depends`, etc.) and let InitO wire the singletons
and services *behind* it.

## A note on `__slots__` and performance

InitO's generated constructors keep CPython's key-sharing instance dict intact,
so attribute access on decorated objects stays at handwritten speed — see
[Performance](performance.md). This holds inside web frameworks too; there is no
per-request or per-instance reflection cost, because all reflection happens once
at import.
