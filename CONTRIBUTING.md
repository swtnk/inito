# Contributing

## Setup

```bash
uv pip install -e ".[dev]"
# or: pip install -e ".[dev]"
pre-commit install
```

## Workflow

```bash
ruff check .            # lint
ruff format .            # format
mypy src                 # typecheck
pytest                   # test + coverage
./scripts/check_all.sh   # all of the above
```

## Standards

Follow `local_dev/engineering.md`'s SOLID/DRY/cognitive-complexity/error-handling
rules and `local_dev/inito.md`'s performance rules (reflection only at
decoration time, generated methods attached once, zero runtime dependencies).
See [CLAUDE.md](./CLAUDE.md) for the architecture map and naming conventions.

## Progress tracking

[TASKS.md](./TASKS.md) is the single source of truth for what's implemented
versus planned. Update its checkboxes as work lands.

## Versioning

Semantic versioning. Version is single-sourced from `src/inito/__init__.py`'s
`__version__`.
