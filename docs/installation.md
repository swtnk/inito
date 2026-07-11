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

If you use mypy, enable inito's bundled plugin so `get_x`/`set_x`,
`__init__`, and `@Builder`'s fluent chain are all correctly typed:

```toml
[tool.mypy]
plugins = ["inito.typing.mypy_plugin"]
```

## Type checking (pyright / Pylance)

pyright has no plugin mechanism, so it sees `@Data`/`@Value`/
`@AllArgsConstructor` constructors natively (via `dataclass_transform` stubs)
but not accessors, `@Builder`, or the other constructors. For **full**
coverage, generate stub files with the bundled tool:

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
