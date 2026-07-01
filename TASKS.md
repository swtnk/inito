# Inito — Implementation Roadmap

Legend: `[x]` done, `[ ]` not started, `[~]` in progress (leave a note next to it)

## Phase 0 — Scaffolding
- [x] Create src-layout package skeleton (`src/inito/{decorators,generators,builders,reflection,typing,metadata,utils,core,exceptions}/__init__.py`)
- [x] Create `tests/` mirrored package skeleton with `conftest.py`
- [x] Create `benchmarks/` skeleton (`conftest.py` + placeholder test file)
- [x] Create `docs/` + `mkdocs.yml` minimal config
- [x] Create `examples/data_basic.py`
- [x] Create `scripts/check_all.sh`
- [x] Write `pyproject.toml` (Hatchling backend, ruff/mypy/pytest/coverage config)
- [x] Fill `LICENSE` with MIT text
- [x] Fill `README.md` with pitch + install + examples (mark unimplemented decorators as planned)
- [x] Write `CHANGELOG.md` (Keep a Changelog format, Unreleased + 0.1.0)
- [x] Write `CONTRIBUTING.md`
- [x] Extend `.gitignore` with Python/tooling ignores
- [x] Write `.pre-commit-config.yaml` (ruff, ruff-format, mypy hooks)
- [x] Write `.github/workflows/ci.yml` (3.9-3.13 matrix: lint, format, typecheck, test, build)
- [x] Write `CLAUDE.md`
- [x] Write this `TASKS.md`
- [x] Add `src/inito/py.typed` marker
- [x] Verify `uv pip install -e ".[dev]"` succeeds locally
- [x] Initial commit

## Phase 1 — Core Engine (metadata + codegen + exceptions)
- [x] `exceptions/errors.py`: `InitoError` hierarchy (7 exception types)
- [x] `exceptions/__init__.py`: re-export all exception types
- [x] `metadata/field.py`: `FieldMetadata` frozen dataclass + `MISSING` sentinel
- [x] `metadata/class_metadata.py`: `ClassMetadata` frozen dataclass + field accessor helpers
- [x] `metadata/extractor.py`: `MetadataExtractor` (annotation/default/inheritance extraction, dataclass-aware, `__inito_metadata__` caching)
- [x] `metadata/__init__.py`: re-export + `default_extractor` singleton
- [x] `reflection/introspection.py`: low-level annotation/MRO walking helpers used by `MetadataExtractor`
- [x] `utils/codegen.py`: `build_function()` source-text+exec() builder
- [x] `utils/decorator_factory.py`: `make_decorator()` dual-mode factory
- [x] `generators/base.py`: `MethodGenerator` + `MultiMethodGenerator` protocols, `GeneratedMethod` value object, `generate_method()`/`generate_methods()` drivers
- [x] `generators/registry.py`: `GeneratorRegistry` class
- [x] `generators/__init__.py`: `default_registry` singleton, capability registration
- [x] `core/attach.py`: `attach_method()` + `attach_capability()` helpers
- [x] Unit tests: `metadata/` (field, class_metadata, extractor) to >95% coverage
- [x] Unit tests: `utils/` (codegen, decorator_factory) to >95% coverage
- [x] Unit tests: `generators/base.py` + `registry.py` to >95% coverage
- [x] Unit tests: `exceptions/errors.py` (raise/catch/message content)
- [x] mypy strict clean on `src/inito/{metadata,utils,generators,core,exceptions,reflection}`
- [x] ruff clean on same

## Phase 2 — @Data (first Initial Feature)
- [x] `generators/constructor.py`: `ConstructorGenerator` (+ shared rendering helpers for future reuse)
- [x] `generators/repr_.py`: `ReprGenerator`
- [x] `generators/equality.py`: `EqGenerator` + `HashGenerator`
- [x] `generators/accessors.py`: `GetterGenerator` + `SetterGenerator`
- [x] Register all 6 capabilities in `generators/__init__.py`
- [x] `decorators/data.py`: `DataOptions` + `_apply_data` + `Data`/`data` export
- [x] `decorators/__init__.py`: re-export `Data`, `data`
- [x] `inito/__init__.py`: public API surface (`Data`, `data`, `InitoError`, `__version__`)
- [x] `examples/data_basic.py`: working runnable example
- [x] Tests: constructor generation (required/defaulted/inherited fields)
- [x] Tests: repr generation (field ordering, repr round-trip readability)
- [x] Tests: eq generation (same class, subclass, different class, `NotImplemented`)
- [x] Tests: hash generation (hashable, equal objects hash equal, usable in sets/dicts)
- [x] Tests: getter/setter generation (all fields, `frozen=True` omits setters)
- [x] Tests: `@Data` bare usage (`@Data`)
- [x] Tests: `@Data(frozen=True)`, `@Data(include_getters=False)`, etc.
- [x] Tests: `@Data` stacked with inheritance (base class fields included)
- [x] Tests: `@Data` stacked on `@dataclass`
- [x] Tests: `@Data` invalid usage (e.g. non-type/non-options argument) raises `DecoratorConfigurationError`
- [x] Tests: metadata caching correctness (decorate once, verify no re-extraction; subclass does not inherit parent's cached metadata incorrectly)
- [x] Verify coverage >95% for `decorators/data.py` and all Phase 2 generators
- [x] mypy strict clean, ruff clean on Phase 2 files
- [x] Manually verify `examples/data_basic.py` runs correctly

## Phase 3 — @Getter
- [x] `decorators/getter.py`: `GetterOptions` + thin wrapper over `"getter"` capability
- [x] Tests + docs example
- [x] Update `inito/__init__.py` exports

## Phase 4 — @Setter
- [x] `decorators/setter.py`: `SetterOptions` + thin wrapper over `"setter"` capability
- [x] Tests + docs example
- [x] Update `inito/__init__.py` exports

## Phase 5 — @NoArgsConstructor
- [x] `generators/constructor.py`: add `NoArgsConstructorGenerator` (reusing shared rendering helpers)
- [x] Register `"no_args_constructor"` capability
- [x] `decorators/no_args_constructor.py`
- [x] Tests (all fields must have defaults or raise `InvalidFieldDefinitionError`) + docs example

## Phase 6 — @AllArgsConstructor
- [x] `decorators/all_args_constructor.py`: thin wrapper over `"constructor"` capability
- [x] Tests + docs example

## Phase 7 — @RequiredArgsConstructor
- [x] `generators/constructor.py`: add `RequiredArgsConstructorGenerator`
- [x] Register `"required_args_constructor"` capability
- [x] `decorators/required_args_constructor.py`
- [x] Tests (defaulted fields excluded from signature, still get default value) + docs example

## Phase 8 — @Builder / builder
- [x] `builders/builder_generator.py`: `BuilderGenerator` (nested Builder class, per-field fluent setters, `build()`, static `builder()` factory attached to owner class)
- [x] `BuilderOptions` (`to_builder`, `setter_prefix`, `build_method_name`)
- [x] Not registered in the shared `GeneratorRegistry` (deliberate deviation: Builder generation depends
      on per-decoration `BuilderOptions`, unlike the fixed-behavior capability generators, so
      `decorators/builder.py` uses `BuilderGenerator` + `core.attach.attach_builder` directly)
- [x] `decorators/builder.py`: `Builder`/`builder` export, supports bare `@builder`, `@builder(to_builder=True)`, stacking under `@dataclass`
- [ ] Typing: generic `Builder[T]` support / IDE-autocomplete review (deferred to Phase 11 — current
      typing is functionally correct but has no `.pyi` stub for fluent-chain autocomplete)
- [x] Tests: fluent chaining, defaults, optional fields, `to_builder=True` pre-population, stacking with `@dataclass`, `setter_prefix`/`build_method_name` options, missing-required-field validation
- [x] Update `examples/` with all three builder example snippets from `local_dev/project.md`
- [x] Verify all 3 `project.md` example snippets run verbatim (`examples/builder_basic.py`; `UUID`
      casing typo from the original spec corrected)

## Phase 9 — @ToString
- [x] `decorators/to_string.py`: `ToStringOptions` + thin wrapper over `"repr"` capability
- [x] Tests + docs example

## Phase 10 — @EqualsAndHashCode
- [x] `decorators/equals_and_hash_code.py`: `EqualsAndHashCodeOptions` + thin wrapper over `"eq"` + `"hash"` capabilities
- [x] Tests + docs example

## Phase 11 — Typing polish pass
- [ ] Add Protocol-based generics review across `builders/`/`typing/` surface
- [ ] Confirm `mypy --strict` and `pyright` both pass on `examples/`
- [ ] Add `.pyi` stub review if needed for builder autocomplete
- [ ] Minimal-`Any` audit across whole `src/`

## Phase 12 — Full test suite to >95% coverage (library-wide)
- [ ] Cross-decorator composition tests (`@Data` + `@Builder` stacking, etc.)
- [ ] Generic class support tests
- [ ] Frozen class tests across all relevant decorators
- [ ] Edge cases: empty class, single field, deeply inherited chains, slots interaction, forward-referenced annotations
- [ ] Invalid usage tests across all decorators
- [ ] Compatibility tests: stacking with dataclasses, with each other
- [ ] Confirm library-wide coverage >95%

## Phase 13 — Benchmarks
- [ ] `benchmarks/`: real pytest-benchmark suite (import time, decoration time, construction, attribute access, builder perf, eq, hash)
- [ ] pyperf-based comparison scripts vs handwritten classes/dataclasses/attrs
- [ ] Memory allocation comparison (tracemalloc-based)
- [ ] Publish results into `docs/performance.md`

## Phase 14 — Documentation
- [ ] `docs/index.md`, `installation.md`, `quickstart.md`
- [ ] `docs/api/` reference pages per decorator
- [ ] `docs/examples/` (mirroring `examples/` directory)
- [ ] `docs/migration.md` (from dataclasses/attrs/Pydantic)
- [ ] `docs/performance.md`
- [ ] `docs/faq.md`, `docs/troubleshooting.md`
- [ ] `mkdocs build` verified clean

## Phase 15 — CI hardening & packaging
- [ ] Verify CI green across all 5 Python versions
- [ ] Add PyPI trusted publishing release workflow (tag-triggered)
- [ ] Dry-run `uv build` + `twine check` locally
- [ ] Version bump workflow documented in `CONTRIBUTING.md`

## Phase 16 — Release
- [ ] Tag v0.1.0
- [ ] Publish to PyPI
- [ ] Verify `pip install inito` and `uv add inito` work post-publish
