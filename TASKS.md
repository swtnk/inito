# Inito — Implementation Roadmap

Legend: `[x]` done, `[ ]` not started, `[~]` in progress (leave a note next to it)

## Phase 0 — Scaffolding
- [x] Create src-layout package skeleton (`src/inito/{decorators,generators,builders,reflection,typing,metadata,utils,core,exceptions}/__init__.py`)
- [x] Create `tests/` mirrored package skeleton with `conftest.py`
- [x] Create `benchmarks/` skeleton (`conftest.py` + placeholder test file)
- [x] Create `docs/` + `mkdocs.yml` minimal config (superseded in Phase 14: migrated to Sphinx +
      Furo, `mkdocs.yml` removed in favor of `docs/conf.py`)
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
- [x] Add Protocol-based generics review across `builders/`/`typing/` surface — reviewed;
      `generators/base.py`'s `MethodGenerator`/`MultiMethodGenerator` Protocols remain the only
      warranted use (a real family of interchangeable generators). `BuilderGenerator` is a single,
      structurally unique implementation — forcing a Protocol onto it would be speculative. `typing/`
      stays intentionally empty pending real generic support (needs the plugin work below).
- [x] Confirm `mypy --strict` passes on `src/` (already true) — **but confirmed it and `pyright`
      both fail on `examples/`** with `reportAttributeAccessIssue`/`attr-defined` for every
      runtime-generated member (`get_x`, `set_x`, `.builder()`, `.to_builder()`, ...). This is
      expected: those members are attached via `setattr` at decoration time, so no static tool can
      see them without a dedicated plugin (the same problem `attrs`/Pydantic solved with mypy
      plugins). Documented as a known v1 limitation rather than worked around; real fix tracked in
      Phase 17.
- [x] `.pyi` stub review for builder autocomplete — reviewed; a per-class `.pyi` isn't feasible for
      a runtime decorator applied to arbitrary user classes without generator/plugin tooling. Real
      fix tracked in Phase 17.
- [x] Minimal-`Any` audit across whole `src/` — reviewed every `Any` usage. Removed two dead
      fallbacks in `metadata/extractor.py` (`hints.get(name, Any)` / `hints.get(field.name,
      field.type)`) that could never actually trigger, since `resolve_type_hints` is all-or-nothing
      (raises `AnnotationResolutionError` rather than returning a partial dict) — replaced with
      direct `hints[name]` indexing (fails fast instead of masking a bug behind a silent fallback).
      All remaining `Any` usages are justified: `FieldMetadata.type_hint`/`default`/`default_factory`
      (arbitrary user-declared types/values — no tighter type exists), generator `build_globals()` →
      `dict[str, Any]` and `codegen.build_function` (the static/dynamic boundary feeding `exec()`),
      and `decorator_factory.make_decorator`'s dual-mode dispatch (already flagged inline with
      `# noqa: ANN401` explaining why).

## Phase 12 — Full test suite to >95% coverage (library-wide)
- [x] Cross-decorator composition tests (`tests/integration/test_composition.py`): `@Data` +
      `@Builder` stacking in both orders, manually composing a `@Data`-equivalent from atomic
      decorators (`@Getter @Setter @EqualsAndHashCode @ToString @AllArgsConstructor`), overlapping
      capabilities (documented: the last-applied/outermost decorator wins), `@Builder` + `@ToString`
      + `@dataclass`
- [x] Generic class support tests (`tests/integration/test_generics.py`): `@Data`/`@Builder` on a
      `Generic[T]` class
- [x] Frozen class tests (`tests/integration/test_frozen.py`): `@Data(frozen=True)`, and — newly
      discovered and documented in README — stacking with `@dataclass(frozen=True)` in either order
      correctly raises `FrozenInstanceError` rather than silently bypassing immutability
- [x] Edge cases (`tests/integration/test_edge_cases.py`): empty class, single field, 3-level
      inheritance, `__slots__` with required-only fields, `__slots__`+default conflicting natively
      in Python (not an inito issue), forward ref to an already-defined class (works), and — newly
      discovered and documented in README — self-referential forward refs fail at decoration time
      since annotations resolve eagerly, before the class's own name is bound
- [x] Invalid usage tests across all 9 decorators, parametrized (`tests/integration/test_invalid_usage.py`):
      non-type/non-options argument, multiple positional arguments, bare vs. `()` call equivalence
- [x] Compatibility tests: stacking with dataclasses covered per-decorator (Phase 2-10) and in
      `test_composition.py`/`test_frozen.py`; stacking with each other covered in `test_composition.py`
- [x] Confirm library-wide coverage >95% (176 tests, 100% line+branch coverage across all of `src/`)

## Phase 13 — Benchmarks
- [x] `benchmarks/`: real pytest-benchmark suite (decoration time, construction, attribute access,
      `@Builder` fluent-chain vs direct construction, `__repr__`, `__eq__`, `__hash__`) comparing
      handwritten/`@Data`/`dataclasses`/`attrs` via a shared `conftest.py` fixture set
      (`point_class`, `point_class_factory`, `builder_point_class`). Added `attrs` + `pyperf` as
      benchmark-only dev dependencies.
- [x] `benchmarks/pyperf_suite.py`: pyperf-based construction comparison vs handwritten
      classes/dataclasses/attrs
- [x] `benchmarks/import_time.py`: subprocess-based cold-import overhead comparison (not originally
      itemized here, but explicitly required by `inito.md`'s benchmarking section)
- [x] `benchmarks/memory_profile.py`: memory allocation comparison (tracemalloc-based)
- [x] Publish results into `docs/performance.md` (added to the docs toctree in Phase 14); notes
      attrs' default `__slots__` memory edge and inito's decoration-time cost as known trade-offs

## Phase 14 — Documentation
- [x] Switched doc tooling from mkdocs to **Sphinx + Furo** (user-requested deviation from
      `inito.md`'s named `mkdocs` tool, made now while only `index.md`/`performance.md` existed —
      cheapest point to switch). Added `sphinx`, `furo`, `myst-parser` dev deps; removed `mkdocs`,
      `mkdocs-material`; removed `mkdocs.yml`; added `docs/conf.py` (MyST markdown support,
      `sphinx.ext.autodoc`/`napoleon`/`viewcode`/`intersphinx`, `myst_heading_anchors = 3`)
- [x] `docs/index.md`, `installation.md`, `quickstart.md`
- [x] `docs/api.md`: curated reference for all 9 decorators + their Options dataclasses (via
      `autodata`/`autoclass`) and the full exception hierarchy — decorators are hand-described
      rather than `autofunction`'d, since they're `make_decorator`-built closures whose introspected
      `(*args, **kwargs)` signature wouldn't be informative
- [x] `docs/examples.md`: every `examples/*.py` embedded via `literalinclude` (can't drift out of
      sync with what actually runs, unlike copy-pasted snippets)
- [x] `docs/migration.md` (from dataclasses/attrs/Pydantic)
- [x] `docs/performance.md` (already written in Phase 13, now linked from the toctree)
- [x] `docs/faq.md`, `docs/troubleshooting.md` (troubleshooting covers the two Phase 12 interaction
      limitations, the Phase 11 typing gap, and the native-Python `__slots__`+default conflict)
- [x] Also added real `__doc__` strings to all 9 public decorator objects (`Data.__doc__ = ...` etc.)
      — needed for a useful `autodata` rendering, and a good side effect: `help(Data)` now works
- [x] `sphinx-build -b html docs <out> -W` verified clean (zero warnings/errors, Furo theme
      confirmed applied, `literalinclude`/`autodoc` output spot-checked)

## Phase 15 — CI hardening & packaging
- [ ] Verify CI green across all 5 Python versions
- [ ] Add PyPI trusted publishing release workflow (tag-triggered)
- [ ] Dry-run `uv build` + `twine check` locally
- [ ] Version bump workflow documented in `CONTRIBUTING.md`

## Phase 16 — Release
- [ ] Tag v0.1.0
- [ ] Publish to PyPI
- [ ] Verify `pip install inito` and `uv add inito` work post-publish

## Phase 17 — mypy/pyright plugin for generated-attribute static typing (post-v1, not blocking release)
- [ ] Design a mypy plugin (`get_type_analyze_hook`/class-decorator hook) that, for each inito
      decorator, synthesizes the generated members (`get_x`/`set_x`, `__init__` signature,
      `.builder()`/`Builder`/`to_builder()`) onto the decorated class's inferred type — the same
      approach `attrs` and Pydantic use for their mypy plugins
- [ ] Register the plugin via `[tool.mypy] plugins = [...]` and document setup in README/docs
- [ ] Investigate an equivalent pyright plugin or type-stub-generation strategy (pyright's plugin
      story differs from mypy's; may require a different approach, e.g. a companion stub generator)
- [ ] Add plugin-specific tests (mypy's plugin test harness) covering every decorator
- [ ] Re-run `mypy --strict` and `pyright` against `examples/` with the plugin enabled and confirm
      they pass cleanly (closing the gap identified in Phase 11)
- [ ] Update TASKS.md/README once this lands to remove the "known limitation" notice
