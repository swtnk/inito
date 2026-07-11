# FastAPI integration

Routes stay ordinary FastAPI functions; a tiny `provide(ServiceType)` helper
turns any registered service into a `Depends`, bridging FastAPI to the InitO
container. `@Config` settings, a `@Singleton` repo, and a `@Service` are wired by
type. Tests use `container.override(...)` to swap a real dependency for a fake.

```bash
uvicorn examples.di.fastapi.app:app
pytest examples/di/fastapi --no-cov
```

A future `Injected[T]` helper (DI 2.0 phase 4) will replace `provide(...)` and
add per-request scope.
