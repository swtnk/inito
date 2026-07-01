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

This is mypy-only — pyright has no equivalent plugin mechanism, though
`@Data`/`@AllArgsConstructor`'s constructors are typed correctly under
pyright too (via a standard `dataclass_transform`-marked stub, no
inito-specific setup needed). See [Troubleshooting](troubleshooting.md) for
the remaining pyright gap.

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
