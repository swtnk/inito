# Redis client injection

A Redis connection is wired as a `@Singleton` (built once, from `@Config`
settings) and injected into a `Cache` service by type. Swap Redis for Valkey by
pointing `REDIS_URL` at a Valkey server — the wiring is identical.

```bash
REDIS_URL=redis://localhost:6379/0 python -m examples.di.redis.services
pytest examples/di/redis --no-cov      # overrides the client with a fake — no server needed
```
