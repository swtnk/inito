# Installation

`inito` has zero runtime dependencies — installing it pulls in nothing else.

```bash
pip install inito
```

or, with [uv](https://docs.astral.sh/uv/):

```bash
uv add inito
```

## Supported Python versions

Python 3.9, 3.10, 3.11, 3.12, and 3.13.

## Type checking (mypy)

If you use mypy, enable InitO's bundled plugin so `get_x`/`set_x`,
`__init__`, and `@Builder`'s fluent chain are all correctly typed:

```toml
[tool.mypy]
plugins = ["inito.typing.mypy_plugin"]
```

## Type checking (pyright / Pylance)

pyright has no plugin mechanism, so it reads `dataclass_transform` (PEP 681)
stubs instead. What that covers **zero-config**, no stubgen needed:

- `@Data` / `@Value` / `@AllArgsConstructor` constructors and their fields.
- `field(default_factory=...)` / `field(default=...)` (declared as
  `field_specifiers`), so a defaulted field is optional in the constructor.
- The **`accessors="attr"`** style end to end — since there are no `get_`/`set_`
  methods to miss, an attr-style `@Data` type-checks with nothing extra.

What still needs stubs under pyright: the Lombok `get_`/`set_` accessors,
`@Builder`'s fluent API (no PEP 681 mechanism models a builder), and
`@NoArgsConstructor`/`@RequiredArgsConstructor` (whose signatures don't match
`dataclass_transform`'s standard semantics). For **full** coverage there, or if
you use Lombok-style accessors, generate stub files with the bundled tool:

```bash
pip install "inito[stubgen]"     # pulls mypy, used only for the base stub
inito-stubgen src/               # writes a .pyi beside each module with inito classes
```

pyright then reads the sibling `.pyi` and sees every generated member. Re-run
it when your decorated classes change (or wire it into pre-commit). Only
pyright users need this step; mypy users rely on the plugin above.

## Development install

To work on `inito` itself:

```bash
git clone https://github.com/swtnk/inito
cd inito
uv pip install -e ".[dev]"   # or: pip install -e ".[dev]"
pre-commit install
```

See [CONTRIBUTING](https://github.com/swtnk/inito/blob/main/CONTRIBUTING.md)
for the full development workflow.
