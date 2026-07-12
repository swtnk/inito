# @Config

Load a class's fields from **environment variables**, coerced to their annotated
types, at construction — then inject the settings object by type.

## The problem it solves

Twelve-factor apps read configuration from the environment, but hand-writing the
plumbing is repetitive and error-prone: `os.environ["PORT"]`, remembering to
`int(...)` it, parsing `"true"`/`"1"` into a bool, applying a default when the
variable is absent, and raising something useful when a required one is missing.
`@Config` derives all of that from the class's annotations, once.

## Usage

```python
from inito import Config


@Config(prefix="APP_")
class Settings:
    database_url: str                 # required  -> reads APP_DATABASE_URL
    port: int = 5432                  # optional  -> APP_PORT, coerced to int
    debug: bool = False               # optional  -> APP_DEBUG, parsed as a bool


settings = Settings()                 # reads os.environ at construction
```

Each field maps to `PREFIX + FIELD_NAME.upper()`. A field with a value in the
environment uses it (coerced); a field without one falls back to its default; a
**required** field with neither raises `ConfigResolutionError`.

Booleans accept `1`/`true`/`yes`/`on` (and `0`/`false`/`no`/`off`),
case-insensitively. `str`, `int`, `float`, and `Optional[...]` are supported;
any other type receives the raw string.

## What it generates

A zero-argument `__init__` that reads the environment and assigns each field.
The field → variable → coercer → default plan is computed **once, at decoration
time**; only the `os.environ` lookups happen at construction (which, for a
singleton, is once).

## Options

| Option | Default | Effect |
|---|---|---|
| `prefix` | `""` | prepended to every field's environment-variable name |

## Use with dependency injection

`@Config` classes are meant to be injected. Register one as a
[`@Service`](../dependency-injection.md) and it is autowired by type into any
constructor that asks for it:

```python
from inito import Config, Service


@Service
@Config(prefix="APP_")
class Settings:
    database_url: str = "sqlite:///app.db"


@Service
class Database:
    def __init__(self, settings: Settings) -> None:
        self.url = settings.database_url
```

See [Configuration injection](../dependency-injection.md#configuration-injection).

## Notes & gotchas

- Values are read from `os.environ` at **construction**, not at import — set the
  environment (or `monkeypatch.setenv(...)` in tests) before the object is built.
- A required field with no environment value and no default raises
  `ConfigResolutionError`; a value that can't be coerced (e.g. `PORT=abc` for an
  `int`) raises it too.
- Need validation, nested config, or `.env` files? A Pydantic `BaseSettings`
  works with InitO's DI the same way — register it as a `@Service` and it
  autowires by type.

## See also

- [Dependency injection](../dependency-injection.md)
- [API reference](../reference/index.md)
