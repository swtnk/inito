# CLAUDE.md

Guidance for working on `inito` in this repository.

## Project summary

`inito` is a Lombok-inspired, zero-runtime-dependency Python library. It
eliminates boilerplate (constructors, `repr`, equality/hashing, accessors,
builders) via decorators that generate real methods once, at class-decoration
time, then attach them directly to the class.

## Authoritative specs

`local_dev/inito.md` (product/technical spec) and `local_dev/engineering.md`
(coding standards) are the governing documents for this project. Both are
gitignored and dev-machine-only — if they're missing on a fresh clone, ask
the user for them before doing feature work. Read them before implementing
anything not already covered here.

## The non-negotiable performance rule

All reflection/annotation inspection happens **exactly once, at decoration
time**. Never inspect annotations or defaults at instance-construction or
method-call time. Generated methods are real Python functions built from
source text via `exec()` and attached directly to the class — never
`__getattr__`/`__getattribute__` overrides, proxies, descriptors, or
monkeypatching after class creation.

Two sanctioned mutation points, and only two:
- `src/inito/utils/codegen.py` (`build_function`) — the only `exec()` call site.
- `src/inito/core/attach.py` (`attach_method` / `attach_capability`) — the
  only place a class is mutated after code generation.

## Naming convention

- Canonical decorator names are PascalCase, matching Lombok and `inito.md`'s
  Initial Features list: `Data`, `Getter`, `Setter`, `Builder`, `ToString`,
  `EqualsAndHashCode`, `NoArgsConstructor`, `AllArgsConstructor`,
  `RequiredArgsConstructor`.
- Each is built by `make_decorator` (a factory function, not a class) so it
  supports both `@Data` and `@Data(frozen=True)`.
- Lowercase aliases are exported bound to the same object (`data = Data`,
  `builder = Builder`, ...) to satisfy the `from inito import builder`
  examples from the spec, while keeping one canonical name.
- Internal generator classes always use the `*Generator` suffix
  (`ConstructorGenerator`, `ReprGenerator`, ...) and are never exported at the
  top level.

## Architecture map

- `decorators/` — public decorators (`@Data`, ...); each is a thin
  ~10–35 line module wiring generators together via `make_decorator`.
- `generators/` — one atomic capability per generator (`constructor`, `repr`,
  `eq`+`hash`, `getter`+`setter`), registered under a capability name in
  `generators/registry.py`.
- `builders/` — the `@Builder` generator (not yet implemented — see Phase 8).
- `reflection/` — low-level MRO/annotation-walking helpers used once by
  `MetadataExtractor`.
- `typing/mypy_plugin/` — the mypy plugin (`fields.py` collects declared
  fields from a class + its bases via mypy's AST, mirroring
  `reflection/introspection.py`'s runtime MRO-walk; `constructors.py`
  synthesizes `__init__`/`get_x`/`set_x` for the constructor/accessor
  decorators; `builder.py` synthesizes the nested `Builder` class via
  `mypy.plugin.SemanticAnalyzerPluginInterface.basic_new_typeinfo`; `options.py`
  reads `@Data(frozen=True)`-style keyword arguments from the decorator call
  expression, since inito's decorators are typed as plain `Callable[...,
  Any]` rather than having a real keyword signature mypy's CallableType-based
  argument lookup could use). Mypy-only — pyright has no third-party plugin
  mechanism.
- `metadata/` — `FieldMetadata`/`ClassMetadata` value types and
  `MetadataExtractor`, which builds and caches metadata once per class.
- `utils/` — `codegen.build_function` and
  `decorator_factory.make_decorator`, the two cross-cutting utilities every
  decorator/generator depends on.
- `core/` — `attach.py`, the sole class-mutation choke point.
- `exceptions/` — the `InitoError` hierarchy.

**How to add a new decorator:** implement a generator (matching the
`MethodGenerator` or `MultiMethodGenerator` protocol in `generators/base.py`),
register it under a new capability name in `generators/__init__.py`, then
write a small decorator module that resolves that capability via
`core.attach.attach_capability` and wraps it with `make_decorator`. Never
modify an existing generator to add a new decorator.

## Commands

```bash
uv pip install -e ".[dev]"   # or: pip install -e ".[dev]"
pytest                        # run tests + coverage
pytest tests/decorators/test_data.py -v   # run a single test file
pytest --cov-report=html       # generate an HTML coverage report
ruff check .                   # lint
ruff format .                  # format
ruff format --check .           # format check (CI mode)
mypy src                        # typecheck
uv build                        # build sdist + wheel
./scripts/check_all.sh          # run all of the above
pytest benchmarks/ --benchmark-only   # run the pytest-benchmark suite
python benchmarks/pyperf_suite.py     # process-isolated pyperf construction comparison
python benchmarks/memory_profile.py   # per-instance memory footprint comparison
python benchmarks/import_time.py      # cold-import overhead comparison
sphinx-build -b html docs docs/_build -W   # build docs, warnings-as-errors
```

## Testing conventions

`tests/` mirrors `src/inito/`'s package structure. Test files are named
`test_<module>.py`. Prefer shared fixtures in `conftest.py` over redefining
sample classes per test file (DRY).

## Progress tracking

`TASKS.md` is the single source of truth for what's implemented versus
planned across sessions. Always update its checkboxes as work completes —
a future session should be able to resume by finding the first unchecked box.
