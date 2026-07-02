# Security & code generation

A common first question about InitO is: *"it calls `exec()` — is that safe to
put in production?"* This page answers that directly.

## Where and when `exec()` runs

InitO has exactly **one** `exec()` call site — `inito.utils.codegen`. Every
decorator assembles a complete `def` block as source text, and that text is
compiled into a real function object **once, at class-decoration time** (when
Python first imports and evaluates your `@Data`/`@Builder`/... class). It never
runs again:

- not at instance construction,
- not at attribute access, `==`, `hash()`, or `repr()`,
- not in response to any runtime input.

After decoration your objects are ordinary instances with ordinary methods.
There is no proxy, no `__getattr__`/`__getattribute__` override, no descriptor
indirection, and no import hook.

## No user input reaches the compiled source

The generated source is assembled from a single kind of input: **the field
names declared in your class's annotations**, which are always valid Python
identifiers. Everything else the generated code needs is passed in through the
function's *globals namespace*, never interpolated into the source string:

- field default values and default factories,
- the owning class's name (used by `__repr__`),
- helper callables such as `object.__setattr__`.

Because values are injected rather than stringified, there is no code-injection
path through your data. Even a class created dynamically with a hostile
`__name__` — e.g. `type('evil"; ...', (), {})`, which a framework metaclass is
free to produce — renders correctly and cannot break compilation or execute
anything. This behaviour is pinned by tests.

## Supply-chain posture

- **Zero runtime dependencies.** Installing `inito` adds no transitive
  packages to your environment.
- **No I/O or network access** at import, decoration, or runtime.
- **No monkeypatching.** InitO only attaches generated methods to the class it
  decorates, via a single choke point (`inito.core.attach`).

## Reporting a vulnerability

See [`SECURITY.md`](https://github.com/swtnk/inito/blob/main/SECURITY.md) in the
repository for the private disclosure process.
