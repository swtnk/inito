# Decorators

inito is a set of small, focused decorators — one per capability, plus the
all-in-one `@Data`. Reach for the smallest one that does what you need; every
page below opens with the specific problem that decorator solves.

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} {octicon}`package` @Data
:link: data
:link-type: doc

The all-in-one: constructor, `__repr__`, `__eq__`, `__hash__`, and
`get_x`/`set_x` accessors.
:::

:::{grid-item-card} {octicon}`lock` @Value
:link: value
:link-type: doc

An immutable data class — `@Data` without setters, frozen on its own.
:::

:::{grid-item-card} {octicon}`arrow-switch` @Getter / @Setter
:link: accessors
:link-type: doc

Lombok-style `get_x()` / `set_x(value)` accessors, and nothing else.
:::

:::{grid-item-card} {octicon}`quote` @ToString
:link: to-string
:link-type: doc

Just a readable `__repr__`.
:::

:::{grid-item-card} {octicon}`git-compare` @EqualsAndHashCode
:link: equals-and-hash-code
:link-type: doc

Value equality and hashing, generated together.
:::

:::{grid-item-card} {octicon}`gear` Constructors
:link: constructors
:link-type: doc

`@NoArgsConstructor`, `@AllArgsConstructor`, and `@RequiredArgsConstructor`.
:::

:::{grid-item-card} {octicon}`tools` @Builder
:link: builder
:link-type: doc

A fluent, chainable builder — `Cls.builder().x(1).build()`.
:::

::::

```{toctree}
:hidden:

data
value
accessors
to-string
equals-and-hash-code
constructors
builder
```
