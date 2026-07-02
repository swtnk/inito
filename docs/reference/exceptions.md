# Exceptions

Every error InitO raises derives from `InitoError`. They are raised at
decoration time (invalid usage/metadata), at `@Builder` build time, or during
dependency resolution — never silently. See
[Troubleshooting](../troubleshooting.md) for worked examples of each.

## Base

```{eval-rst}
.. autoclass:: inito.InitoError
   :members:
```

## Metadata and code generation

```{eval-rst}
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
```

## Builder

```{eval-rst}
.. autoclass:: inito.exceptions.BuilderValidationError
   :members:
```

## Dependency injection

```{eval-rst}
.. autoclass:: inito.exceptions.DependencyRegistrationError
   :members:

.. autoclass:: inito.exceptions.UnresolvableDependencyError
   :members:

.. autoclass:: inito.exceptions.CircularDependencyError
   :members:
```
