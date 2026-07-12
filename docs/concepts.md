# Concepts: the problem InitO solves

## The boilerplate problem

Every data-carrying Python class needs the same mechanical methods written
over and over: a constructor that assigns each field, a `__repr__` for
debugging, `__eq__`/`__hash__` so instances compare and hash by value, and —
if you like accessors — a getter and setter per field. For a five-field
class that is easily forty lines of code that says nothing interesting, is
tedious to keep in sync when a field is added, and is a common source of
bugs (a field forgotten in `__eq__`, a stale `__repr__`).

```python
# Written by hand — every line is mechanical, and drifts when fields change:
class User:
    def __init__(self, name, email, age=0):
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name, self.email, self.age) == (other.name, other.email, other.age)

    def __hash__(self):
        return hash((self.name, self.email, self.age))

    def get_name(self): return self.name
    def set_name(self, value): self.name = value
    # ... and get/set for email and age
```

```python
# The same thing with inito:
from inito import Data


@Data
class User:
    name: str
    email: str
    age: int = 0
```

`dataclasses` solves part of this, but it is all-or-nothing (you take its
whole bundle) and it does not generate `get_x`/`set_x` accessors or a fluent
builder. InitO takes an à-la-carte approach instead: one focused decorator per
capability, plus an all-in-one `@Data`. You reach for exactly the pieces a class
needs — only a builder, only accessors, only the constructor — and pay for
nothing else.

## How InitO solves it — without the usual runtime cost

The naive way to "generate methods" in Python is to intercept attribute
access at runtime (`__getattr__`, descriptors, proxies). That is flexible
but slow: every access pays for the machinery.

InitO never does that. **All reflection happens exactly once, at
decoration time.** Each decorator reads the class's annotations, builds the
source text of a real Python function, compiles it with `exec()`, and
attaches the resulting function object to the class — just as if you had
typed it. At runtime there is no InitO left in the picture: your objects are
ordinary instances, and the generated `__init__`/`__eq__`/`get_x` run the
exact bytecode a handwritten version would.

The result is code that reads like three lines but performs like forty. See
[Performance](performance.md) for the measured numbers (construction,
attribute access, `==`, and `hash()` are all at handwritten/`dataclasses`
parity).

## The two ideas to keep in mind

1. **One decorator, one job.** `@Data` is a convenience bundle; underneath
   it are atomic decorators (`@Getter`, `@ToString`, `@EqualsAndHashCode`,
   the constructors, ...) you can apply individually. Reach for the smallest
   one that does what you need.
2. **Decoration-time only.** Adding a field changes what gets generated the
   next time the module is imported — never at runtime. There is nothing to
   "keep in sync": the generated methods are always derived from the current
   fields.

## Where to go next

- [Quick start](quickstart.md) — a fast tour of every decorator.
- **Decorators** (in the sidebar) — a dedicated page per decorator with the
  specific problem it solves, its options, and gotchas.
- [Dependency injection](dependency-injection.md) — wiring object graphs.
- [Recipes](recipes.md) — real-world, combined patterns.
