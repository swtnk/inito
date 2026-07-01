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
