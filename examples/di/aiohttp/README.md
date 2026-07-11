# aiohttp integration

Async handlers resolve services from the InitO container per request; tested with
aiohttp's built-in test utilities. `@Config` settings, a `@Singleton` repo, and a
`@Service` are wired by type and swapped for fakes via `container.override(...)`.

```bash
python -m examples.di.aiohttp.app       # serves on :8080
pytest examples/di/aiohttp --no-cov
```
