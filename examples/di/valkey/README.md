# Valkey client injection

Identical wiring to the [redis example](../redis/), using the `valkey` client
(Valkey is a Redis fork). A `@Singleton` client built from `@Config` settings is
injected into a `Cache` service.

```bash
VALKEY_URL=valkey://localhost:6379/0 python -m examples.di.valkey.services
pytest examples/di/valkey --no-cov      # overrides the client with a fake — no server needed
```
