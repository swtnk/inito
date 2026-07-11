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

## Later batches
- [ ] Sanic, Aiohttp (web, async handlers via `@Inject`)
- [ ] Django (services/views; ORM stays framework-owned)
- [ ] Valkey (same as Redis, different URL), RabbitMQ (pika/aio-pika connection)
- [ ] Deepen web examples with per-request scope + pooled-resource lifecycle
      once DI 2.0 phases 3–4 land (Resources, Scopes, `Injected[T]` FastAPI helper)
