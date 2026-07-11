---
name: gate
description: Run inito's full quality gate (ruff lint, ruff format check, mypy strict, pytest with coverage, and the Sphinx docs -W build) and report pass/fail concisely. Use before committing a nontrivial change, before a release, or when the user asks to "run the checks / gate / full check". Does not modify code.
---

# gate

Run every check CI runs, locally, and report crisply.

## Steps
Activate the project venv, then run (stop-and-report on first hard failure, but
prefer running all so the report is complete):

```bash
source .venv/bin/activate
ruff check .
ruff format --check .
mypy src
pytest -q
sphinx-build -b html docs docs/_build -W
```

## Report
One line per check with pass/fail, plus for pytest the test count and coverage %
(must be ≥ 95%). If anything fails, show the minimal failing output and stop for
a fix — do not "fix and rerun" silently.

## Notes
- Coverage floor is 95% (`--cov-fail-under=95` in pyproject); the suite is
  normally ~97–98%.
- For a release-grade check, also verify Python 3.9 in a throwaway venv
  (`uv venv --python 3.9 …` + `uv pip install -e ".[dev]"`) — runtime-annotation
  issues have regressed only on 3.9 before.
- Interop tests (Pydantic/SQLAlchemy/Django) need the `interop` extra installed;
  they `importorskip` otherwise.
