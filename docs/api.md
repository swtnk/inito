# API reference

Every decorator supports three call styles: `@Data`, `@Data()`, and
`@Data(option=value, ...)`. Every decorator is also exported under a
lowercase alias (`Data`/`data`, `Builder`/`builder`, ...) bound to the exact
same object — use whichever reads better in your code. Each section below
names both forms explicitly.

## @Data / data

```{eval-rst}
.. autodata:: inito.Data
   :annotation:

.. autoclass:: inito.DataOptions
   :members:
```

Also exported as `inito.data` (the same object).

## @Getter / getter

```{eval-rst}
.. autodata:: inito.Getter
   :annotation:

.. autoclass:: inito.GetterOptions
   :members:
```

Also exported as `inito.getter` (the same object).

## @Setter / setter

```{eval-rst}
.. autodata:: inito.Setter
   :annotation:

.. autoclass:: inito.SetterOptions
   :members:
```

Also exported as `inito.setter` (the same object).

## @NoArgsConstructor / no_args_constructor

```{eval-rst}
.. autodata:: inito.NoArgsConstructor
   :annotation:

.. autoclass:: inito.NoArgsConstructorOptions
   :members:
```

Also exported as `inito.no_args_constructor` (the same object).

## @AllArgsConstructor / all_args_constructor

```{eval-rst}
.. autodata:: inito.AllArgsConstructor
   :annotation:

.. autoclass:: inito.AllArgsConstructorOptions
   :members:
```

Also exported as `inito.all_args_constructor` (the same object).

## @RequiredArgsConstructor / required_args_constructor

```{eval-rst}
.. autodata:: inito.RequiredArgsConstructor
   :annotation:

.. autoclass:: inito.RequiredArgsConstructorOptions
   :members:
```

Also exported as `inito.required_args_constructor` (the same object).

## @Builder / builder

```{eval-rst}
.. autodata:: inito.Builder
   :annotation:

.. autoclass:: inito.BuilderOptions
   :members:
```

Also exported as `inito.builder` (the same object) — this is the form used
throughout the [Quick start](quickstart.md) and [Examples](examples.md) pages.

## @ToString / to_string

```{eval-rst}
.. autodata:: inito.ToString
   :annotation:

.. autoclass:: inito.ToStringOptions
   :members:
```

Also exported as `inito.to_string` (the same object).

## @EqualsAndHashCode / equals_and_hash_code

```{eval-rst}
.. autodata:: inito.EqualsAndHashCode
   :annotation:

.. autoclass:: inito.EqualsAndHashCodeOptions
   :members:
```

Also exported as `inito.equals_and_hash_code` (the same object).

## @Value / value

```{eval-rst}
.. autodata:: inito.Value
   :annotation:

.. autoclass:: inito.ValueOptions
   :members:
```

Also exported as `inito.value` (the same object). Generates a constructor,
`__repr__`, `__eq__`, `__hash__`, and `get_` accessors — never setters.
Stack with `@dataclass(frozen=True)` for genuine attribute-write
immutability; on its own `@Value` only omits setters, it doesn't block
direct attribute assignment.

## Dependency injection: Container, @Service, @Singleton, @Inject

```{eval-rst}
.. autoclass:: inito.Container
   :members:

.. autoclass:: inito.Scope
   :members:

.. data:: inito.default_container

   The shared Container that @Service/@Singleton register into by default.

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
register a class's constructor dependency types at decoration time —
they never mutate the class, so it remains an ordinary, directly
constructible Python class; `container.get(cls)` is the DI-aware path
that autowires and lazily builds it. See
[Quick start](quickstart.md#dependency-injection) for a worked example
and the per-call cost of `@Inject`.

## Exceptions

```{eval-rst}
.. autoclass:: inito.InitoError
   :members:

.. autoclass:: inito.exceptions.MetadataExtractionError
   :members:

.. autoclass:: inito.exceptions.AnnotationResolutionError
   :members:

.. autoclass:: inito.exceptions.InvalidFieldDefinitionError
   :members:

.. autoclass:: inito.exceptions.CodeGenerationError
   :members:

.. autoclass:: inito.exceptions.DecoratorConfigurationError
   :members:

.. autoclass:: inito.exceptions.DuplicateGeneratorError
   :members:

.. autoclass:: inito.exceptions.BuilderValidationError
   :members:

.. autoclass:: inito.exceptions.DependencyRegistrationError
   :members:

.. autoclass:: inito.exceptions.UnresolvableDependencyError
   :members:

.. autoclass:: inito.exceptions.CircularDependencyError
   :members:
```
