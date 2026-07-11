# Configuration injection (`@Config`)

`@Config(prefix="APP_")` generates a constructor that loads each field from an
environment variable (`APP_DATABASE_URL`, `APP_PORT`, `APP_DEBUG`), coerced to
the annotated type. Registered as a `@Service`, the settings object is autowired
by type into anything that depends on it — no globals, no `Provide[]` markers.

```bash
APP_PORT=9000 APP_DEBUG=true python -m examples.di.settings.app
pytest examples/di/settings --no-cov
```
