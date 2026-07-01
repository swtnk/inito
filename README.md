# inito

A Lombok-inspired boilerplate-elimination library for Python. `inito`
generates constructors, `repr`, equality/hashing, accessors, and (soon)
fluent builders once at class-decoration time — never at instance
construction or attribute-access time — so the generated classes perform
like handwritten ones. Zero runtime dependencies.

## Install

```bash
pip install inito
```

or

```bash
uv add inito
```

## Quick start

```python
from inito import Data


@Data
class User:
    name: str
    age: int = 0


user = User("Ada", age=30)
print(user)              # User(name='Ada', age=30)
print(user.get_name())   # Ada
user.set_age(31)
```

`@Data` also accepts options:

```python
from inito import Data


@Data(frozen=True)
class Point:
    x: int
    y: int
```

## Status

Implemented today: `@Data` (constructor, `__repr__`, `__eq__`, `__hash__`,
getters, setters) and `@Getter` (getters only).

Planned (see [TASKS.md](./TASKS.md) for the full roadmap): `@Setter`,
`@NoArgsConstructor`, `@AllArgsConstructor`, `@RequiredArgsConstructor`,
`@Builder`/`builder`, `@ToString`, `@EqualsAndHashCode`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT — see [LICENSE](./LICENSE).
