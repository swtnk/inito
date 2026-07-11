# Sanic integration

Async Sanic handlers resolve services from the InitO container per request;
tested with `sanic-testing`. Dependencies are swapped for fakes via
`container.override(...)`.

```bash
sanic examples.di.sanic.app:app
pytest examples/di/sanic --no-cov
```
