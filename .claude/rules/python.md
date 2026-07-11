# inito coding standards

Every change must meet these. Generated code must be indistinguishable from the
team's own. (Full source: `local_dev/engineering.md`, dev-machine-only; this is
the tracked distillation.)

## Architecture (non-negotiable — inito-specific)
- **Reflect once, at decoration/registration time.** Never inspect annotations,
  defaults, or signatures at instance-construction or method-call time.
- **Two, and only two, mutation points:** `utils/codegen.py::build_function`
  (the only `exec()`) and `core/attach.py` (the only place a class is mutated
  after codegen). Never `__getattr__`/`__getattribute__`, proxies, descriptors,
  or post-hoc monkeypatching.
- **Zero runtime dependencies.** Third-party frameworks (Pydantic, YAML, FastAPI)
  are optional, duck-typed paths — never imported unconditionally in `src/`.
- **Decorator naming:** canonical PascalCase (`Data`, `Builder`) built by
  `make_decorator`; lowercase alias bound to the same object (`data = Data`);
  internal generators use the `*Generator` suffix and are never exported.
- **Add a capability, don't modify an existing generator.** New behavior = new
  generator + capability registration + a thin decorator wired via
  `attach_capability`/`make_decorator`.

## Code
- **Immutable by default** (`@dataclass(frozen=True)`); optional types over
  `None`-sentinels where a value may be absent.
- **Self-documenting names; no explanatory inline comments.** A comment earns its
  place only for a non-obvious *why* (a subtle invariant), never a *what*.
- **Docstrings:** concise Google-style, one line where possible; document purpose,
  not implementation. No redundant param restatements.
- **DRY:** centralize shared logic; reuse generators, metadata models, utilities.
- **Cognitive complexity < 14** per function (ruff `C90`); early returns over deep
  nesting.
- **Few parameters:** group related config into a frozen `*Options` dataclass.
- **Small, cohesive, deterministic functions/classes; minimal public API.**
- **Fail fast:** raise meaningful `InitoError` subclasses; no silent failures, no
  broad `except`, never suppress unexpected exceptions.
- **stdlib-first**; justify any new dependency (there are none at runtime).

## Gates (must pass — the `gate` skill runs these)
`ruff check .` · `ruff format --check .` · `mypy src` (strict) · `pytest`
(coverage ≥ 95%) · `sphinx-build -b html docs docs/_build -W`. Runtime-eval'd
annotations must stay valid on **Python 3.9** (no PEP 604 `X | None` in a
string/forward-ref that gets `eval`'d) through **3.14**.

## Tests
`tests/` mirrors `src/inito/`; files `test_<module>.py`; shared fixtures in
`conftest.py`. Prefer **dependency-free** tests (duck-typed fakes) so they run on
the whole version matrix; real-framework tests go in the interop suite/CI job.
