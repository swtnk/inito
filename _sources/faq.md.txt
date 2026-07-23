# FAQ

## Why not just use `dataclasses`?

You often should — see [Migration: from dataclasses](migration.md#from-dataclasses).
`inito` adds accessors, a fluent builder, and the ability to pick individual
capabilities (`@Getter` alone, `@ToString` alone, ...) rather than one
all-or-nothing decorator.

## Does `inito` validate field values?

No. `inito` generates boilerplate (constructors, `repr`, equality, hashing,
accessors, builders) — it never inspects or validates the *values* passed
in, only the *declared fields* (once, at decoration time). If you need
validation, that belongs in `__post_init__` (works fine alongside
`@dataclass`), a custom `__init__` override, or a dedicated validation
library.

## Is it safe to use `@Data` in a hot path?

Yes — see [Performance](performance.md). Reflection and code generation
happen exactly once, at decoration time. Constructing instances, reading
attributes, comparing, and hashing all run the same generated Python
bytecode a handwritten class would, with no per-call overhead.

## Can I add my own methods to a decorated class?

Yes, normally:

```python
from inito import Data


@Data
class User:
    name: str
    age: int

    def greet(self) -> str:
        return f"Hello, {self.name}"
```

`inito` only ever attaches the specific members each decorator is
responsible for (e.g. `@Data` never touches a method you define yourself
under a name it doesn't generate, like `greet`). It will overwrite a method
it *does* generate (e.g. `__repr__`) if you also define one by hand,
since decoration always attaches its generated version last.

## Why does `@Builder` alone not give me a nice `repr`?

By design — see the [`@ToString` + `@Builder` example](decorators/to-string.md).
Each decorator does one focused thing; stack `@ToString` (or `@Data`) alongside
`@Builder` for a readable repr.

## Are the decorator names related to Lombok?

If you've used [Lombok](https://projectlombok.org/) in Java, InitO's decorator
names (`@Data`, `@Builder`, `@Getter`, `@Value`, `@RequiredArgsConstructor`, …)
will look familiar — they follow the same naming so the mental model carries
over. That's the only connection: InitO is a standalone, pure-Python library
with its own implementation and design, not a port.

## Does `inito` work with generic classes (`Generic[T]`)?

Yes — decorating a `Generic[T]` class works normally; `inito` only inspects
declared fields, not type-parameter machinery.
