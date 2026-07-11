# Framework-examples showcase

A dependency-injector-style gallery of runnable apps wiring InitO's DI into real
frameworks/clients, each with a smoke test (external clients `override`n with
fakes) and a README. Lives in `examples/di/`; runs in a dedicated CI `examples`
job via the `examples` extra.

Legend: `[x]` done · `[ ]` todo

## Batch 1 (done)
- [x] `examples/di/settings/` — `@Config` env settings, autowired
- [x] `examples/di/redis/` — Redis client as `@Singleton`, injected into `Cache`
- [x] `examples/di/boto3/` — boto3 S3 client as `@Singleton`, injected into `Storage`
- [x] `examples/di/fastapi/` — routes via a `provide()` Depends bridge; override-tested
- [x] `examples` extra (fastapi/httpx/redis/boto3); CI `examples` job; `examples/di/README.md` index
- [x] mypy-examples regression scoped to top-level `examples/*.py` (framework files excluded)
- [ ] Docs "Examples" showcase page (fold into the Phase 1 docs pass)

## Batch 2 (done)
- [x] `examples/di/valkey/` — Valkey client (Redis fork) as `@Singleton` → `Cache`
- [x] `examples/di/rabbitmq/` — pika connection `@Singleton` → `Publisher` (params
      only until a channel opens, so the graph resolves without a broker)
- [x] `examples/di/aiohttp/` — async handlers resolve per request; aiohttp test utils
- [x] `examples/di/sanic/` — async handlers resolve per request; sanic-testing
- [x] `examples/di/django/` — a view resolves a service; Django test client
- [x] `examples` extra + CI job extended; index README updated. 21 example tests pass.

## Later
- [ ] Deepen web examples with per-request scope + pooled-resource lifecycle
      once DI 2.0 phases 3–4 land (Resources, Scopes, `Injected[T]` FastAPI helper)
