# API reference

The complete public API of InitO (the `inito` package). Every decorator
supports three call styles — `@Data`, `@Data()`, and `@Data(option=value,
...)` — and every PascalCase decorator has a lowercase alias (`Data`/`data`,
`Builder`/`builder`, ...) bound to the exact same object; use whichever reads
better.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`package` Decorators
:link: decorators
:link-type: doc

`@Data`, `@Value`, accessors, `@ToString`, `@EqualsAndHashCode`, the
constructor decorators, and `@Builder`.
:::

:::{grid-item-card} {octicon}`plug` Dependency injection
:link: dependency-injection
:link-type: doc

`Container`, `Scope`, `default_container`, `@Service`/`@Component`,
`@Singleton`, and `@Inject`.
:::

:::{grid-item-card} {octicon}`alert` Exceptions
:link: exceptions
:link-type: doc

The `InitoError` hierarchy raised at decoration, build, and resolution time.
:::

::::

For task-oriented documentation, see the [User Guide](../user-guide.md).

```{toctree}
:hidden:

decorators
dependency-injection
exceptions
```
