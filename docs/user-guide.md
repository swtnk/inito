# User Guide

This guide explains InitO's decorators and how to use them. For the complete
list of every symbol, option, and exception, see the
[API reference](reference/index.md).

## Getting started

- [Installation](installation.md) — install InitO and enable the mypy plugin.
- [Concepts](concepts.md) — the boilerplate problem InitO solves, and how it
  stays fast.
- [Quick start](quickstart.md) — a guided tour of every decorator.

## Decorators

InitO is a set of small, focused decorators — one per capability, plus the
all-in-one `@Data`.

- [@Data](decorators/data.md) — constructor, `repr`, `eq`/`hash`, accessors.
- [@Value](decorators/value.md) — an immutable, setter-free data class.
- [Accessors](decorators/accessors.md) — `@Getter` / `@Setter`.
- [@ToString](decorators/to-string.md) — a readable `__repr__`.
- [@EqualsAndHashCode](decorators/equals-and-hash-code.md) — value equality
  and hashing.
- [Constructors](decorators/constructors.md) — `@NoArgsConstructor`,
  `@AllArgsConstructor`, `@RequiredArgsConstructor`.
- [@Builder](decorators/builder.md) — a fluent, chainable builder.

## Dependency injection

- [Dependency injection](dependency-injection.md) — `@Service`/`@Singleton`/
  `@Inject` and the `Container`.

## Recipes and guides

- [Recipes](recipes.md) — real-world, combined-decorator patterns.
- [Examples](examples.md) — the runnable scripts from the repository.
- [Migration](migration.md) — coming from `dataclasses` or `attrs`.

## Help

- [Performance](performance.md) — benchmarks vs. handwritten/`dataclasses`.
- [FAQ](faq.md) — common questions.
- [Troubleshooting](troubleshooting.md) — errors and how to fix them.

```{toctree}
:caption: Getting started
:hidden:

installation
concepts
quickstart
```

```{toctree}
:caption: Decorators
:hidden:

decorators/data
decorators/value
decorators/accessors
decorators/to-string
decorators/equals-and-hash-code
decorators/constructors
decorators/builder
```

```{toctree}
:caption: Dependency injection
:hidden:

dependency-injection
```

```{toctree}
:caption: Recipes and guides
:hidden:

recipes
examples
migration
```

```{toctree}
:caption: Help
:hidden:

performance
faq
troubleshooting
```
