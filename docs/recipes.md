# Recipes

Real-world, copy-pasteable patterns that combine several decorators. Every
snippet on this page is executed as-is by the test suite, so it runs exactly
as shown. For a single-decorator tour see [Quick start](quickstart.md); for
the standalone runnable scripts see [Examples](examples.md).

## Immutable value object

Use `@Value` for small, comparable, hashable values that should never change
after construction — money, coordinates, identifiers. It is immutable on its
own, with no `@dataclass(frozen=True)` needed.

```python
from dataclasses import FrozenInstanceError
from inito import Value


@Value
class Money:
    amount: int
    currency: str = "USD"


price = Money(500)
print(price)                       # Money(amount=500, currency='USD')
print(price == Money(500, "USD"))  # True
print(price.get_currency())        # USD  (getters, but never setters)

try:
    price.amount = 0               # immutable
except FrozenInstanceError:
    print("cannot mutate a @Value")

# Hashable, so it works as a dict key or set member:
totals = {Money(500): "five dollars"}
```

## Configuration object with defaults and a mutable default

Required fields first, defaulted fields after — the same ordering Python
uses. For a **mutable** default (a list, dict, set), stack `@dataclass` so
InitO picks up `field(default_factory=...)`; each instance then gets its own
fresh container.

```python
from dataclasses import dataclass, field
from inito import Data


@Data
@dataclass
class ServerConfig:
    host: str = "localhost"
    port: int = 8080
    tags: list = field(default_factory=list)


config = ServerConfig(port=9000)
print(config)                      # ServerConfig(host='localhost', port=9000, tags=[])
ServerConfig().tags.append("a")
print(ServerConfig().tags)         # []  — a fresh list per instance, not shared
```

## Fluent builder for a request/response model

`@Builder` shines when a type has several optional fields and you want
readable, order-independent construction. `to_builder=True` also adds a
`.to_builder()` for deriving a modified copy.

```python
from dataclasses import dataclass
from inito import Builder


@Builder(to_builder=True)
@dataclass
class HttpRequest:
    method: str
    url: str
    timeout: float = 30.0
    retries: int = 0


request = (
    HttpRequest.builder()
    .method("GET")
    .url("/users")
    .timeout(5.0)
    .build()
)
print(request.timeout)             # 5.0

# Derive a variant without mutating the original:
with_retries = request.to_builder().retries(3).build()
print(with_retries.retries, request.retries)   # 3 0
```

## Service layer with dependency injection

`@Singleton`/`@Service` register classes; `@Inject` fills a function's
annotated parameters from the container. A parameter is autowired only if its
type is a registered service — plain values (`page_size: int`) keep their own
defaults. Combine with `@RequiredArgsConstructor` so a field annotation is
all you need, no hand-written `__init__`.

```python
from inito import Service, Singleton, Inject, RequiredArgsConstructor, default_container


@Singleton
class Database:
    rows = {1: "Ada", 2: "Linus"}   # seed data — no constructor needed


@Service
@RequiredArgsConstructor
class UserRepository:
    db: Database                    # autowired

    def name(self, user_id: int) -> str:
        return self.db.rows[user_id]


@Service
@RequiredArgsConstructor
class Greeter:
    repo: UserRepository            # autowired, transitively

    def greet(self, user_id: int) -> str:
        return f"Hello, {self.repo.name(user_id)}"


@Inject
def handle(greeter: Greeter) -> None:
    print(greeter.greet(1))         # Hello, Ada


handle()

# The same graph, resolved explicitly:
print(default_container.get(Greeter).greet(2))   # Hello, Linus

# Every @Service class is still an ordinary class you can build by hand:
manual = Greeter(UserRepository(Database()))
```

## Transient scope and an isolated container

Singletons are cached; `Scope.TRANSIENT` rebuilds on every resolution. Use a
dedicated `Container` (instead of the shared `default_container`) to keep a
subsystem's registrations isolated — handy in tests.

```python
from inito import Service, Scope
from inito.di import Container


container = Container()


@Service(scope=Scope.TRANSIENT, container=container)
class RequestContext:
    def __init__(self) -> None:
        self.token = object()


a = container.get(RequestContext)
b = container.get(RequestContext)
print(a is b)                      # False — a fresh instance each time
print(container.is_registered(RequestContext))   # True
```

## Compose exactly the capabilities you want

`@Data` is a bundle; when you want less, stack the atomic decorators. This
class gets a repr, value equality, and read-only accessors — but no
constructor and no setters.

```python
from inito import ToString, EqualsAndHashCode, Getter


@ToString
@EqualsAndHashCode
@Getter
class Point:
    x: int
    y: int


p = Point()
p.x, p.y = 1, 2
print(p)                # Point(x=1, y=2)
print(p.get_x())        # 1
print(p == p)           # True
```

## Inheritance

Fields accumulate across the MRO, base-class fields first — so a subclass
constructor takes the base's fields followed by its own.

```python
from inito import Data


@Data
class Animal:
    name: str


@Data
class Dog(Animal):
    breed: str


rex = Dog("Rex", "Labrador")
print(rex)              # Dog(name='Rex', breed='Labrador')
print(rex.name, rex.breed)   # Rex Labrador
```

## Add your own methods

InitO only attaches the members each decorator owns; anything else you write
is left untouched, so decorated classes are just normal classes.

```python
from inito import Data


@Data
class Temperature:
    celsius: float

    def to_fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32


t = Temperature(20)
print(t.to_fahrenheit())    # 68.0
print(t)                    # Temperature(celsius=20)
```
