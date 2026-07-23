# Decorators

API reference for every code-generating decorator. For usage, options, and
examples, see the corresponding [User Guide](../user-guide.md) page linked
from each section.

## field

```{eval-rst}
.. autofunction:: inito.field
```

Declare a field's default explicitly — the inito-native equivalent of
`dataclasses.field`. Use `field(default_factory=...)` for a mutable default
(a bare `items: list = []` is rejected) and `field(default=...)` for a plain
one. Recognized by the mypy plugin and by pyright (PEP 681 `field_specifiers`),
so the annotated field type still checks.

## @Data / data

```{eval-rst}
.. autodata:: inito.Data
   :annotation:

.. autoclass:: inito.DataOptions
   :members:
```

Also exported as `inito.data`. Guide: [@Data](../decorators/data.md).

## @Value / value

```{eval-rst}
.. autodata:: inito.Value
   :annotation:

.. autoclass:: inito.ValueOptions
   :members:
```

Also exported as `inito.value`. Generates a constructor, `__repr__`,
`__eq__`, `__hash__`, and `get_` accessors — never setters, and genuinely
immutable (assignment/deletion raise `dataclasses.FrozenInstanceError`), with
no `@dataclass(frozen=True)` stacking. Guide: [@Value](../decorators/value.md).

## @Getter / getter

```{eval-rst}
.. autodata:: inito.Getter
   :annotation:

.. autoclass:: inito.GetterOptions
   :members:
```

Also exported as `inito.getter`. Guide: [Accessors](../decorators/accessors.md).

## @Setter / setter

```{eval-rst}
.. autodata:: inito.Setter
   :annotation:

.. autoclass:: inito.SetterOptions
   :members:
```

Also exported as `inito.setter`. Guide: [Accessors](../decorators/accessors.md).

## @ToString / to_string

```{eval-rst}
.. autodata:: inito.ToString
   :annotation:

.. autoclass:: inito.ToStringOptions
   :members:
```

Also exported as `inito.to_string`. Guide: [@ToString](../decorators/to-string.md).

## @EqualsAndHashCode / equals_and_hash_code

```{eval-rst}
.. autodata:: inito.EqualsAndHashCode
   :annotation:

.. autoclass:: inito.EqualsAndHashCodeOptions
   :members:
```

Also exported as `inito.equals_and_hash_code`.
Guide: [@EqualsAndHashCode](../decorators/equals-and-hash-code.md).

## @NoArgsConstructor / no_args_constructor

```{eval-rst}
.. autodata:: inito.NoArgsConstructor
   :annotation:

.. autoclass:: inito.NoArgsConstructorOptions
   :members:
```

Also exported as `inito.no_args_constructor`.
Guide: [Constructors](../decorators/constructors.md).

## @AllArgsConstructor / all_args_constructor

```{eval-rst}
.. autodata:: inito.AllArgsConstructor
   :annotation:

.. autoclass:: inito.AllArgsConstructorOptions
   :members:
```

Also exported as `inito.all_args_constructor`.
Guide: [Constructors](../decorators/constructors.md).

## @RequiredArgsConstructor / required_args_constructor

```{eval-rst}
.. autodata:: inito.RequiredArgsConstructor
   :annotation:

.. autoclass:: inito.RequiredArgsConstructorOptions
   :members:
```

Also exported as `inito.required_args_constructor`.
Guide: [Constructors](../decorators/constructors.md).

## @Builder / builder

```{eval-rst}
.. autodata:: inito.Builder
   :annotation:

.. autoclass:: inito.BuilderOptions
   :members:
```

Also exported as `inito.builder`. Guide: [@Builder](../decorators/builder.md).

## @Config / config

```{eval-rst}
.. autodata:: inito.Config
   :annotation:

.. autoclass:: inito.ConfigOptions
   :members:
```

Also exported as `inito.config`. Guide: [@Config](../decorators/config.md).

## @Jsonize / jsonize

```{eval-rst}
.. autodata:: inito.Jsonize
   :annotation:

.. autoclass:: inito.JsonizeOptions
   :members:
```

Also exported as `inito.jsonize`. Generates `to_dict()`/`to_json()` serializing
every declared field (datetime, UUID, Decimal, Enum, bytes, Path, nested
`@Jsonize`, …) to JSON-native forms. Guide: [@Jsonize](../decorators/jsonize.md).
