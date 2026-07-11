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
| [`valkey/`](valkey/) | The same wiring with a Valkey client (Redis fork) |
| [`boto3/`](boto3/) | A boto3 S3 client wired as a `@Singleton`, injected into a `Storage` service |
| [`rabbitmq/`](rabbitmq/) | A RabbitMQ (pika) connection `@Singleton` injected into a `Publisher` |
| [`fastapi/`](fastapi/) | FastAPI routes resolving services via a `Depends` bridge to the container |
| [`aiohttp/`](aiohttp/) | Async aiohttp handlers resolving services per request |
| [`sanic/`](sanic/) | Async Sanic handlers resolving services per request |
| [`django/`](django/) | A Django view resolving a service from the container |

Every web example is override-tested (a real dependency swapped for a fake). The
web examples gain per-request scope + pooled-resource lifecycle once DI 2.0
phases 3–4 land (plus an `Injected[T]` FastAPI helper).

## Run

```bash
pip install -e ".[examples]"            # fastapi, aiohttp, sanic, django, redis, valkey, boto3, pika, ...

python -m examples.di.settings.app       # prints resolved settings (no external deps)
uvicorn examples.di.fastapi.app:app      # serves the FastAPI app

pytest examples/di --no-cov              # run every example's smoke test
```

The client-backed `main()` entry points expect a real server/credentials; the
smoke tests don't — they override the client with a fake to exercise the wiring.
