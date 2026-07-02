# Security Policy

## Supported versions

Security fixes are released for the latest published version of `inito`. Please
upgrade to the most recent release before reporting an issue.

## Reporting a vulnerability

Please report suspected vulnerabilities privately rather than opening a public
issue:

- Use GitHub's **[Report a vulnerability](https://github.com/swtnk/inito/security/advisories/new)**
  (Security → Advisories) to open a private advisory, **or**
- email **swetanksubham.r@gmail.com** with the details.

Include a description, affected version(s), and a minimal reproduction if
possible. You can expect an initial acknowledgement within a few days. Once a
fix is available it will be released and the advisory published with credit to
the reporter (unless you prefer to remain anonymous).

## How `inito` uses code generation

`inito` generates methods (`__init__`, `__repr__`, accessors, builders, ...)
from source text via a single `exec()` call site
(`src/inito/utils/codegen.py`), **once per decorated class at
class-decoration time** — never at instance construction or attribute-access
time, and never in response to runtime input.

The generated source is assembled only from **field names taken from a class's
own annotations** (always valid Python identifiers). No user-supplied *values*
are ever interpolated into the compiled source: defaults, default factories,
and the owning class name are passed into the generated function through its
globals namespace, not baked into the source string. A class built dynamically
with an unusual `__name__` (for example by a framework metaclass) therefore
cannot break compilation or inject code.

`inito` has **zero runtime dependencies**, performs no I/O, no network access,
and no monkeypatching of other modules. It never overrides
`__getattr__`/`__getattribute__` and installs no import hooks.
