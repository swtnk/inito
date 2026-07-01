# API reference

Every decorator supports three call styles: `@Data`, `@Data()`, and
`@Data(option=value, ...)`. Lowercase aliases (`data`, `getter`, `builder`,
...) are the same object as their PascalCase name — use whichever reads
better in your code.

## @Data

```{eval-rst}
.. autodata:: inito.Data
   :annotation:

.. autoclass:: inito.DataOptions
   :members:
```

## @Getter

```{eval-rst}
.. autodata:: inito.Getter
   :annotation:

.. autoclass:: inito.GetterOptions
   :members:
```

## @Setter

```{eval-rst}
.. autodata:: inito.Setter
   :annotation:

.. autoclass:: inito.SetterOptions
   :members:
```

## @NoArgsConstructor

```{eval-rst}
.. autodata:: inito.NoArgsConstructor
   :annotation:

.. autoclass:: inito.NoArgsConstructorOptions
   :members:
```

## @AllArgsConstructor

```{eval-rst}
.. autodata:: inito.AllArgsConstructor
   :annotation:

.. autoclass:: inito.AllArgsConstructorOptions
   :members:
```

## @RequiredArgsConstructor

```{eval-rst}
.. autodata:: inito.RequiredArgsConstructor
   :annotation:

.. autoclass:: inito.RequiredArgsConstructorOptions
   :members:
```

## @Builder / builder

```{eval-rst}
.. autodata:: inito.Builder
   :annotation:

.. autoclass:: inito.BuilderOptions
   :members:
```

## @ToString

```{eval-rst}
.. autodata:: inito.ToString
   :annotation:

.. autoclass:: inito.ToStringOptions
   :members:
```

## @EqualsAndHashCode

```{eval-rst}
.. autodata:: inito.EqualsAndHashCode
   :annotation:

.. autoclass:: inito.EqualsAndHashCodeOptions
   :members:
```

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
```
