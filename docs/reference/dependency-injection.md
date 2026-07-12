# Dependency injection

API reference for the DI subsystem. For the full guide (resolution, scopes,
containers, errors, and the thread-safety/performance guarantees) see
[Dependency injection](../dependency-injection.md).

## Container and Scope

```{eval-rst}
.. autoclass:: inito.Container
   :members:

.. autoclass:: inito.Scope
   :members:

.. autoclass:: inito.Qualifier
   :members:

.. autoclass:: inito.Factory
   :members:

.. data:: inito.default_container

   The shared Container that ``@Service``/``@Singleton`` register into by
   default.
```

`Container` exposes `get`/`aget`/`register`/`register_provider`/`is_registered`/
`reset`, `scope()` (a `with`/`async with` scope for `Scope.SCOPED` services), the
resource lifecycle `shutdown_resources`/`ashutdown_resources` (and the
`with`/`async with` context-manager protocol), and the test overrides
`override`/`override_factory`/`overrides`/`clear_override`/`clear_overrides`.
`Scope` adds `SCOPED` (one instance per `scope()`). `Scope` is `SINGLETON`, `TRANSIENT`, or `THREAD_LOCAL`.
`Qualifier` names an implementation for `Annotated[Base, Qualifier("name")]`.
`Factory[T]` injects a callable that builds a fresh `T` per call, autowiring its
registered dependencies and taking the rest as call-time keyword arguments.

## Decorators

```{eval-rst}
.. autodata:: inito.Service
   :annotation:

.. autoclass:: inito.ServiceOptions
   :members:

.. autodata:: inito.Singleton
   :annotation:

.. autodata:: inito.Inject
   :annotation:

.. autofunction:: inito.Resource

.. autoclass:: inito.ResourceOptions
   :members:

.. autoclass:: inito.Injected
```

`@Resource` marks a class (torn down by `close()`/`aclose()` or the
`__enter__`/`__exit__` protocol) or a generator-provider function (`yield` the
resource, then clean up) whose lifetime the `Container` manages. Tear resources
down with `container.shutdown_resources()` / `with container`, or
`await container.ashutdown_resources()` / `async with container` for async ones;
an async generator provider is built with `await container.aget(cls)`.

Also exported as `inito.component`/`inito.Component` (a literal alias for
`@Service`), `inito.singleton`, and `inito.inject`. `@Service`/`@Singleton`
register a class's constructor dependency types at decoration time — they
never mutate the class, so it stays an ordinary, directly-constructible
Python class; `container.get(cls)` is the DI-aware path that autowires and
lazily builds it.
