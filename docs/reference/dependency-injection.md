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

.. data:: inito.default_container

   The shared Container that ``@Service``/``@Singleton`` register into by
   default.
```

`Container` exposes `get`/`register`/`is_registered`/`reset`, and the test
overrides `override`/`override_factory`/`overrides`/`clear_override`/
`clear_overrides`. `Scope` is `SINGLETON`, `TRANSIENT`, or `THREAD_LOCAL`.
`Qualifier` names an implementation for `Annotated[Base, Qualifier("name")]`.

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
```

Also exported as `inito.component`/`inito.Component` (a literal alias for
`@Service`), `inito.singleton`, and `inito.inject`. `@Service`/`@Singleton`
register a class's constructor dependency types at decoration time — they
never mutate the class, so it stays an ordinary, directly-constructible
Python class; `container.get(cls)` is the DI-aware path that autowires and
lazily builds it.
