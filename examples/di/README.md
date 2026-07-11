# InitO dependency injection — framework examples

Small, runnable apps showing InitO's DI wiring real frameworks and clients — the
zero-dependency, annotation-native way (no `Provide[]` markers, no provider
objects; just `@Service`/`@Singleton`/`@Config` and type annotations).

Each example builds a `Container`, wires services by type, and ships a smoke test
that proves the wiring resolves (external clients are `override`n with fakes, so
no live server/DB is needed).

## Examples

| Example | Shows |
|---|---|
| [`settings/`](settings/) | `@Config` loads settings from the environment, autowired by type |
| [`redis/`](redis/) | A Redis client wired as a `@Singleton`, injected into a `Cache` service |
| [`boto3/`](boto3/) | A boto3 S3 client wired as a `@Singleton`, injected into a `Storage` service |
| [`fastapi/`](fastapi/) | FastAPI routes resolving services via a `Depends` bridge to the container; tested with overrides |

More frameworks (Django, Sanic, Aiohttp, Valkey, RabbitMQ, …) are on the way, and
the web examples gain per-request scope + pooled-resource lifecycle once DI 2.0
phases 3–4 land.

## Run

```bash
pip install -e ".[examples]"            # fastapi, httpx, redis, boto3

python -m examples.di.settings.app       # prints resolved settings (no external deps)
uvicorn examples.di.fastapi.app:app      # serves the FastAPI app

pytest examples/di --no-cov              # run every example's smoke test
```

The `redis`/`boto3` `main()` entry points expect a real server/credentials; the
smoke tests don't — they override the client with a fake to exercise the wiring.
