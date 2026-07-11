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
sphinx-build -b html docs docs/_build -W   # build docs, warnings-as-errors
```

## Standards

Follow `local_dev/engineering.md`'s SOLID/DRY/cognitive-complexity/error-handling
rules and `local_dev/inito.md`'s performance rules (reflection only at
decoration time, generated methods attached once, zero runtime dependencies).
See [CLAUDE.md](./CLAUDE.md) for the architecture map and naming conventions.

## Progress tracking

[dev/README.md](./dev/README.md) is the entry point for ongoing work — it links
the roadmap, active task checklists, and decision log. Update the active
`dev/tasks/phase-*.md` checkboxes and `dev/README.md` as work lands. The finished
build history lives in [dev/history.md](./dev/history.md).

## Versioning

Semantic versioning. Version is single-sourced from `src/inito/__init__.py`'s
`__version__` — hatchling reads it via a regex, so bumping it there is the
only place that needs to change.

## Release process

1. Bump `__version__` in `src/inito/__init__.py`, following semver.
2. Update `CHANGELOG.md`: move the `[Unreleased]` entries under a new
   `[X.Y.Z] - YYYY-MM-DD` heading.
3. Commit, then tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. Pushing a `v*` tag triggers `.github/workflows/release.yml`, which builds
   the sdist/wheel, runs `twine check`, and publishes to PyPI via trusted
   publishing (OIDC) — no API token needed in CI.

**One-time setup required before the first release** (not something CI or
this repo's config can do on its own):

- On [PyPI](https://pypi.org/manage/account/publishing/), register a
  "trusted publisher" for the `inito` project pointing at this repo, the
  `release.yml` workflow filename, and a `pypi` environment name (this can
  be done *before* the first release — PyPI supports pending publishers for
  projects that don't exist yet).
- In the GitHub repo settings, create an environment named `pypi` (matches
  `release.yml`'s `environment: name: pypi`) — optionally with protection
  rules (e.g. required reviewers) before it can publish.

Without that one-time PyPI-side setup, `release.yml`'s publish job will
fail with an OIDC/trusted-publisher authentication error — that's expected
until the trusted publisher is registered.
