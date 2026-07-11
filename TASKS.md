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
- [x] Typing: generic `Builder[T]` support / IDE-autocomplete review — resolved for mypy by Phase 17's
      mypy plugin (`typing/mypy_plugin/builder.py` synthesizes a real nested `Builder` type with
      correctly-typed fluent setters and `build()`, giving genuine autocomplete/type-checking in any
      mypy-aware editor integration). **Still an open gap for pyright/Pylance specifically** — the
      backend most VS Code users get autocomplete from — since pyright has no third-party plugin
      mechanism; tracked honestly as a permanent limitation in Phase 17, not re-opened here
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
- [x] Frozen class tests (`tests/integration/test_frozen.py`): `@Data(frozen=True)`, and stacking with
      `@dataclass(frozen=True)` in either order. **Revised after initial release**: originally this
      phase found construction itself raised `FrozenInstanceError` and documented that as "expected,
      not a bug" — a real user hit this in practice and prompted reconsidering it. Fixed by having
      generated constructors (`@Data`'s `__init__`, `@Builder`'s `build()`, `@NoArgsConstructor`/
      `@RequiredArgsConstructor`) assign fields via `object.__setattr__` instead of plain assignment,
      mirroring exactly how a real frozen dataclass's own `__init__` bypasses its blocking
      `__setattr__` for initial construction. Setters deliberately kept as plain assignment, so
      post-construction mutation still correctly fails — only construction is exempted.
      **Revised again in 0.0.8-beta**: `@Data(frozen=True)` originally only skipped setter
      generation, silently allowing `point.x = 5` to succeed directly — a second user-reported bug
      (this time against `@Value`, see Phase 18) showed this didn't match real immutability
      expectations. Both `@Data(frozen=True)` and `@Value` now attach a generated
      `__setattr__`/`__delattr__` pair (new `generators/immutability.py` capability, registered as
      `"immutable"`) that unconditionally raises `FrozenInstanceError` — no `@dataclass(frozen=True)`
      stacking needed for either. Required no change to any constructor generator, since they already
      bypass `__setattr__` via `object.__setattr__`
- [x] Edge cases (`tests/integration/test_edge_cases.py`): empty class, single field, 3-level
      inheritance, `__slots__` with required-only fields, `__slots__`+default conflicting natively
      in Python (not an inito issue), forward ref to an already-defined class (works), and
      self-referential forward refs (e.g. linked-list `next: Node`) — fixed in 0.0.5-beta via a
      temporary module-dict injection in `resolve_type_hints`, decoration-time-only, no added
      per-instance/per-call cost; see README's "Self-referential fields" section
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
- [x] **Performance pass in 0.0.11-beta** (prompted by a requested code review, written up in
      `local_dev/review.md`): (1) `@Inject` no longer calls `Signature.bind_partial()` per call —
      precomputes each param's (name, positional-index, resolved-type) once at decoration time,
      ~4x faster (~830ns → ~200ns). (2) DI container resolves dependencies before taking a
      service's construction lock, eliminating a cross-thread cyclic deadlock. (3)
      `docs/performance.md` construction/DI numbers re-measured — the old construction row predated
      the 0.0.4 `object.__setattr__` change and understated the cost
- [x] **Performance pass follow-up in 0.0.12-beta** (second review round): the 0.0.11 attempt to
      speed up construction via a `self.__dict__["x"] = x` write was found to be a **net
      regression** — it breaks CPython's key-sharing instance dict (PEP 412), silently slowing
      every attribute read (+~40%) and `__eq__`/`__hash__`/`__repr__` (+~80%), which are far hotter
      than construction. Reverted to a plain `self.x = x` for ordinary classes (fastest *and*
      key-sharing-friendly) with a once-bound `object.__setattr__` only for immutable classes
      (detected via `generators/constructor.py::needs_object_setattr`, an MRO walk for an overridden
      `__setattr__`; `@Value`/`@Data(frozen=True)` now attach immutability *before* the constructor
      so it's detected). Net: inito reaches handwritten/dataclasses parity on construction AND reads
      AND eq/hash/repr. Cost: stacking `@dataclass(frozen=True)` *outermost* (after inito) is no
      longer supported — construction raises, since inito generates its constructor before that
      decorator runs and can't detect it; use the innermost order or `@Value`/`@Data(frozen=True)`.
      Also fast-pathed the warm `Container.get()` (single dict lookup, ~79ns → ~45ns). `@Builder`'s
      `build()` keeps `object.__setattr__` unconditionally (it can't detect immutability applied by
      a later decorator like `@Value @Builder`, and object.__setattr__ preserves key-sharing anyway)

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
- [x] Verify CI green across all 5 Python versions — verified **locally** first (built a throwaway
      venv per version: 3.9, 3.10, 3.11, 3.13; 3.12 already covered by the main `.venv` — all green,
      176 tests, 100% coverage). Once pushed to the real GitHub remote, the actual CI run failed on
      every matrix leg with `uv pip install --system`: Ubuntu's runner Python at `/usr` is PEP
      668-protected ("externally managed"), and `--system` targets it directly rather than the
      matrix-selected version `setup-uv` prepared. Fixed by switching to `uv venv --python
      <version>` + `uv pip install -e ".[dev]"`, then `uv run <command>` for every subsequent step
      (ruff/mypy/pytest/sphinx-build); `twine`'s install-then-invoke (same `--system` problem)
      replaced with `uvx twine check dist/*` in both `ci.yml` and `release.yml`. Re-verified by
      reproducing every CI step locally against a clean `git archive` checkout (not the dev `.venv`)
      for Python 3.9 — install, lint, format-check, mypy, pytest, docs build, `uv build`, and `uvx
      twine check` all pass. Also bumped `actions/checkout` v4→v7, `astral-sh/setup-uv` v3→v8,
      `actions/upload-artifact`/`download-artifact` v4→v7/v8 in both workflow files, since GitHub's
      Node 20 deprecation notice flagged the old pins as still targeting the retiring runtime.
- [x] Add PyPI trusted publishing release workflow (tag-triggered): `.github/workflows/release.yml`
      (`build` job → `uv build` + `twine check`; `publish` job → OIDC trusted publishing via
      `pypa/gh-action-pypi-publish`, no stored API token). Validated with `@action-validator/cli`
      (via `bunx`) alongside `ci.yml`. **Requires one-time manual PyPI + GitHub setup before it can
      actually publish** — documented in `CONTRIBUTING.md`'s new "Release process" section (register
      a trusted publisher on PyPI, create a `pypi` GitHub environment) — not something achievable
      from this environment.
- [x] Dry-run `uv build` + `twine check` locally — both `PASSED` on the built sdist and wheel
- [x] Version bump workflow documented in `CONTRIBUTING.md` (new "Release process" section: bump
      `__version__`, update `CHANGELOG.md`, tag `vX.Y.Z`, push triggers `release.yml`)

## Phase 16 — Release
- [x] Tag v0.0.1-beta
- [x] Publish to PyPI — https://pypi.org/project/inito/, version `0.0.1b0`, published via
      `release.yml`'s OIDC trusted-publishing flow (one retry needed: the first attempt failed with
      `invalid-publisher` because the PyPI trusted publisher wasn't registered yet — fixed by adding
      it with Owner `swtnk`, Repository `inito`, Workflow `release.yml`, Environment `pypi`, then
      re-running the same failed job — no new tag needed since nothing had been uploaded yet)
- [x] Verify `pip install inito` and `uv add inito` work post-publish — verified via `uv pip install
      inito==0.0.1b0` into a fresh throwaway venv (not the dev checkout): resolved with zero
      dependencies, `@Data`/`@builder` composition works correctly against the real published wheel

## Phase 17 — mypy plugin for generated-attribute static typing (mypy done; pyright partially closed)
- [x] Built a real mypy plugin at `src/inito/typing/mypy_plugin/` using `get_class_decorator_hook_2`,
      grounded directly against the installed mypy 1.20.2's own source (`mypy/plugin.py`,
      `mypy/plugins/common.py`, and mypy's own bundled `dataclasses.py`/`attrs.py` plugins as
      reference implementations) rather than guessed API usage:
  - `fields.py`: `collect_fields()` walks the class + its MRO for plain annotated attributes
    (ClassVar-excluded), mirroring `reflection/introspection.py`'s runtime algorithm exactly, but
    over mypy's AST/`TypeInfo` model instead of real `__annotations__`
  - `constructors.py`: synthesizes `__init__` (required-then-defaulted ordering) and `get_x`/`set_x`
    for `@Data`/`@Getter`/`@Setter`/`@NoArgsConstructor`/`@AllArgsConstructor`/`@RequiredArgsConstructor`,
    including a real `ctx.api.fail(...)` error for `@NoArgsConstructor` on a field without a default
  - `builder.py`: synthesizes a genuine nested `Builder` class via
    `basic_new_typeinfo` (the same technique mypy's own attrs plugin uses for its internal
    magic-attribute class) with real fluent setters returning the Builder's own type, a
    `build()`/custom-named method returning the owner's type, a `builder()` classmethod, and an
    optional `to_builder()` — full support for `setter_prefix`/`build_method_name`/`to_builder` options
  - `options.py`: reads `@Data(frozen=True)`-style keyword arguments directly from the decorator call
    expression, since inito's decorators are plain `Callable[..., Any]` (built by `make_decorator`)
    rather than having a real keyword signature the CallableType-based lookup mypy's bundled
    attrs/dataclasses plugins use could work against
  - `@ToString`/`@EqualsAndHashCode` deliberately have **no** registered hook: empirically confirmed
    (via `reveal_type`) that mypy already retains full class identity through an
    `Any`-returning class decorator, so `__repr__`/`__eq__`/`__hash__` are already correctly typed
    with zero plugin help needed
- [x] Registered both PascalCase and lowercase fullnames for all 7 hooked decorators (14 registrations)
      so `@Data`/`@data`, `@builder`/`@Builder`, etc. both work — verified this matters, since mypy
      resolves decorator hooks by the definition-site fullname of the referenced symbol, and
      `Data`/`data` are separate `Var` symbols even though they're the same runtime object
- [x] Documented setup in README (new "Type checking" section) and `docs/installation.md`/`docs/troubleshooting.md`
- [x] Investigated pyright: **no third-party mypy-plugin equivalent exists** — confirmed empirically
      (`pyright --strict` on `examples/` still shows the full original 90-error baseline, unaffected by
      the mypy plugin, as expected). Closing this would need a fundamentally different strategy (e.g. a
      companion `.pyi`-stub generator) — not attempted here, tracked as a real, permanent, documented gap
      rather than a to-do, since pyright's plugin architecture doesn't support this the way mypy's does
- [x] Added 22 plugin-specific tests (`tests/mypy_plugin/`) using `mypy.api.run()` **in-process**
      (not subprocess) so coverage.py actually tracks execution of the new plugin code — covers every
      hooked decorator's typing behavior, inheritance, `ClassVar` exclusion, ordering, ambient wrong-type/
      wrong-arg-count/unknown-attribute error detection, ambient `@Data`+`@Builder` composition, and a
      dedicated regression test asserting all of `examples/*.py` pass `mypy --strict` with the plugin
      enabled. 97% overall coverage maintained (the plugin's own uncovered lines are all the same
      `return False`/"mypy multi-pass placeholder not ready yet, defer" guard — a real but
      not-worth-force-testing path, same category as similar guards already accepted elsewhere)
- [x] Re-ran `mypy --strict` against `examples/`: **0 errors** (down from 16 in Phase 11) — verified
      against both our pinned `mypy>=1.11,<2` and, in a fresh install, the newest `mypy==2.1.0`
- [x] One known, documented cosmetic quirk: `reveal_type()` on a `Builder` instance itself shows a
      doubled qualname (e.g. `Point.Point.Builder`) due to how mypy's printer formats synthetic nested
      classes; doesn't affect real error messages (already correctly say `Point.Builder`) or
      type-checking correctness — not chased further given the effort/value tradeoff
- [x] **Partial pyright fix, added afterward**: `decorators/data.pyi` and `decorators/all_args_constructor.pyi`
      mark `Data`/`AllArgsConstructor` with standard `typing.dataclass_transform` (PEP 681, which both
      mypy and pyright understand natively — no plugin needed), giving pyright a correctly-typed
      constructor for these two. Modeled directly on `attrs`' own `.pyi` stub (two `@overload`s per
      decorator: bare-class-arg form and keyword-options form, each marked with the transform) rather
      than guessed. Verified end-to-end from a real installed wheel (not just the editable dev checkout)
      that both mypy and pyright correctly catch missing/extra constructor arguments and still show
      `reveal_type` as the real class, not `Any`
- [x] Deliberately did **not** apply this to `NoArgsConstructor`/`RequiredArgsConstructor`: built throwaway
      probes proving `dataclass_transform`'s standard semantics don't match either decorator's real
      constructor behavior (`NoArgsConstructor` truly takes zero arguments, not "every field optional";
      `RequiredArgsConstructor` excludes defaulted fields from `__init__` entirely, not "optional") — both
      probes showed pyright/mypy would silently *accept* a call the real generated `__init__` rejects at
      runtime if marked this way. A misleading type is worse than an honest gap, so these two decorators
      keep the plain (unmarked) gap rather than gaining an incorrect one
- [x] Added `typing-extensions` as an explicit dev dependency (used only inside `.pyi` stubs, never
      executed at runtime — it was already a transitive dependency of `mypy` itself, but made explicit
      for dev-environment clarity rather than silently relying on another package's dependency chain)

## Phase 18 — @Value (from Future Features, implemented ahead of the rest)

`inito.md`'s "Future Features" list marks `@Value` (and the rest of that
list) "should not be implemented yet." User explicitly requested `@Value`
be built anyway, ahead of Phase 19's DI work, since it's a thin composition
of already-registered capabilities (no new generator needed) rather than a
new subsystem. The other Future Features (`@Immutable`, `@Singleton`,
`@Inject`, `@Lazy`, `@Factory`, `@Proxy`, `@Delegate`, `@Validate`,
`@Observable`, `@Cached`, `@Retry`, `@Timed`) remain deliberately
unimplemented.

- [x] `decorators/value.py`: `ValueOptions` (`include_getters`), `_apply_value`
      wiring the existing `constructor`/`repr`/`eq`/`hash`/`getter` capabilities
      (no new generator needed at the time — reuses the same `ConstructorGenerator`
      `@Data`/`@AllArgsConstructor` already use; a new `"immutable"` generator was
      added later, see below) — never generates setters, unlike `@Data`, which
      only omits them when `frozen=True` is passed explicitly
- [x] `decorators/value.pyi`: `typing.dataclass_transform` stub (PEP 681, same
      pattern as `data.pyi`/`all_args_constructor.pyi`) — pyright gets a
      correctly-typed constructor with no inito-specific plugin needed
- [x] mypy plugin: `transform_value` in `constructors.py` (reuses `add_init`/
      `add_getters`), registered under both `Value`/`value` fullnames in
      `mypy_plugin/__init__.py`
- [x] Exported from `decorators/__init__.py` and top-level `inito/__init__.py`
- [x] `examples/value_basic.py`: plain-class and `@dataclass(frozen=True)`-stacked
      usage (auto-picked-up by the `tests/mypy_plugin/test_examples_regression.py`
      glob and mypy-plugin coverage)
- [x] Tests: `tests/decorators/test_value.py` (bare usage, `include_getters=False`,
      inheritance, stacking with `@dataclass(frozen=True)` confirming real
      immutability, invalid-argument rejection, options defaults) and
      `tests/mypy_plugin/test_value.py` (init/getter typing, missing-arg error,
      setters never generated, `include_getters=False`, inheritance)
- [x] Docs: `docs/api.md`, `docs/quickstart.md`, `docs/examples.md`,
      `docs/troubleshooting.md` (added to the pyright `dataclass_transform`
      exception list), README Status section
- [x] **Revised in 0.0.8-beta**: initially `@Value` only omitted setters, same as
      `@Data(frozen=True)` — it did *not* block direct attribute assignment
      without also stacking a real `@dataclass(frozen=True)` underneath, which
      didn't match Lombok's `@Value` (unconditionally immutable, no extra
      annotation). A real user hit this via `@Value @Builder class Person: ...`
      then `person.name = "Bob"` silently succeeding. Fixed by adding a new
      `"immutable"` generator capability (`generators/immutability.py`) that
      `@Value` now always attaches (and `@Data(frozen=True)` attaches too, see
      Phase 12) — a generated `__setattr__`/`__delattr__` pair unconditionally
      raising `FrozenInstanceError`. `@dataclass(frozen=True)` stacking still
      works but is no longer required for either decorator

## Phase 19 — Dependency injection: @Service/@Inject/@Singleton

`inito.md`'s "Future Features" list names `@Singleton`, `@Inject`, `@Lazy`,
`@Factory` and says explicitly not to implement them yet, only to keep the
architecture extensible. Raised in conversation: Lombok's
`@RequiredArgsConstructor` enables Spring-style constructor DI in Java, but
that wiring is Spring's IoC container doing the work, not Lombok itself —
so an equivalent in Python needs a real DI container, not just a
constructor-generating decorator. Pulled forward (like `@Value` in Phase
18) by explicit user request, ahead of the rest of the Future Features
list. This is the library's **first genuinely new kind of state**: every
prior decorator is purely per-class, computed once at decoration time with
no cross-class coordination; a `Container` is process-wide and lazy.

- [x] `src/inito/di/container.py`: a stateful `Container` (registrations
      dict keyed by class object, singleton-instance cache dict) plus a
      shared `default_container` singleton, mirroring `GeneratorRegistry`'s
      register/get shape
- [x] **Revised in 0.0.10-beta**: originally shipped with no thread-locking
      ("matches the project's zero-runtime-dependency/no-locking-elsewhere
      posture"), documented as a known v1 limitation. A user explicitly
      asked whether `@Singleton` was thread/process-safe; verified
      empirically with real `threading`/`multiprocessing` reproductions
      that it was **not** thread-safe (20 concurrent threads racing a cold
      `get()` produced 20 separate constructions and 20 distinct
      instances — a genuine check-then-act race with no lock) before
      confirming (as expected, and inherent to any pure in-memory Python
      object, not something to "fix") that a singleton is always
      per-process, never shared across OS processes. Fixed the thread
      race via double-checked locking: a per-class `threading.Lock`
      (lazily created behind a small shared "lock of locks" guard),
      acquired only on the cold path — the already-benchmarked warm/cached
      `get()` path is untouched (no lock acquired at all if the singleton
      is already cached), confirmed via `benchmarks/test_di_benchmark.py`
      showing no regression on the warm-cache numbers. `stdlib threading`
      only, no new dependency. **Further hardened in 0.0.11-beta**: the
      original 0.0.10 version held a service's lock across its entire
      recursive dependency resolution, which left a narrow cross-thread
      deadlock (two threads resolving a cyclic graph from opposite ends).
      Fixed by resolving dependencies *before* taking the service's lock, so
      no thread ever holds two locks at once — each thread's own `path`
      catches the cycle and raises `CircularDependencyError` cleanly, and
      the critical section shrinks to just construct-and-cache. Verified with
      a concurrent-cycle stress test that now raises instead of hanging
- [x] `@Service`/`@Component` (`decorators/service.py`) registers a class's
      constructor dependency types into a container **at decoration time**
      (via `resolve_constructor_dependencies`, reusing `make_decorator`)
      without instantiating anything — never mutates the class, so it
      remains an ordinary, directly-constructible Python class
- [x] Lazy resolution: `container.get(cls)` resolves the dependency graph
      and builds instances bottom-up on first request, via a private
      `_resolve(cls, path)` that threads an explicit path tuple for
      circular-dependency detection (not relying on set-iteration order).
      `Container.get` is a real generic method (`type[T] -> T`), correctly
      typed under mypy/pyright natively — no plugin/`.pyi` stub needed
- [x] Scope semantics: `Scope.SINGLETON` (default, cached after first
      resolution) vs. `Scope.TRANSIENT` (rebuilt every `get()`).
      `@Singleton` is a standalone decorator (not a stacking requirement
      on `@Service`) that rejects an explicit conflicting `scope=` kwarg
      loudly rather than silently honoring it
- [x] **Resolved design decision**: a constructor parameter is autowired
      only if its annotated type is itself registered; if unregistered but
      it has a default value, the default applies (the param is simply
      omitted from the resolved kwargs); if unregistered with no default,
      `UnresolvableDependencyError` at `get()`-time. Every parameter must
      still be type-annotated - that's checked at `register()`/decoration
      time via `DependencyRegistrationError`, since it's import-order
      independent. This lets `@Service` classes mix real dependencies and
      plain config (`DatabaseService(repo: UserRepo, port: int = 5432)`)
- [x] **Revised in 0.0.9-beta**: `resolve_constructor_dependencies` originally
      only inspected `__init__`'s own annotations, which works for a
      hand-written constructor but not for one *generated* by
      `@RequiredArgsConstructor`/`@AllArgsConstructor`/`@Data`/
      `@NoArgsConstructor` — their `exec()`'d source never carries
      annotations (they only ever needed parameter names). A real user hit
      this stacking `@Service @RequiredArgsConstructor`. Fixed by falling
      back to the `ClassMetadata` that decorator already cached on the
      class (`cls.__dict__[METADATA_ATTRIBUTE]`) whenever a parameter name
      has no `__init__` annotation — reuses existing decoration-time
      reflection rather than re-deriving anything, and requires no new
      per-call or per-instance work
- [x] Discovery: **explicit registration only in v1** (services register
      purely as an import side effect) — no `scan_package()`/classpath-scan
      helper, matching "Python has no classpath-scanning equivalent"
- [x] Circular-dependency detection at graph-build time (`get()`-time, not
      registration-time, since cycles can span services registered in any
      order) — `CircularDependencyError`, message includes the full cycle
      path. Covered for 2-node, 3-node, and self-referential cycles
- [x] `@Inject` (`decorators/inject.py`) wraps a function (not a class) so
      its type-annotated, unfilled parameters are resolved from a
      container per call — explicitly **not** zero-overhead, unlike every
      other decorator (documented in `docs/quickstart.md`/
      `docs/performance.md`), since it's a composition-root/entry-point
      boundary, not a hot-path generated method. Signature/hints are
      inspected once at decoration time; only `bind_partial` + per-unfilled
      -param `container.get()` happen per call
- [x] Tests: `tests/di/test_container.py` (23 tests: roundtrip, duplicate
      registration, singleton caching, transient scope, nested graphs,
      2/3-node and self cycles, transient-under-singleton sharing,
      mixed config/dependency resolution, unannotated-param rejection,
      `reset()`, container independence), `tests/di/test_dependency_resolver.py`
      (7 tests), `tests/decorators/test_service.py`/`test_singleton.py`/
      `test_inject.py` (16 tests) — 100% line+branch coverage on every new
      module. New `tests/conftest.py` autouse fixture resets
      `default_container` before/after every test, since it's the first
      process-wide mutable state in the test suite
- [x] Benchmarks (`benchmarks/test_di_benchmark.py`): attribute access on a
      container-resolved instance is at parity with hand-written (22.7ns vs
      22.5ns - the real "zero overhead after construction" claim); warm
      singleton `get()`, cold full-graph resolution, and `@Inject` call
      overhead are all measured against hand-written equivalents and found
      to have real, quantified (not hidden) costs - see
      `docs/performance.md`'s dedicated DI section
- [x] Docs: `docs/api.md`, `docs/quickstart.md` (new "Dependency injection"
      section covering config-vs-dependency params, scope semantics, and
      the `@Inject` overhead caveat), `docs/examples.md` +
      `examples/di_basic.py`, `docs/troubleshooting.md` (new
      `CircularDependencyError`/`UnresolvableDependencyError`/
      `DependencyRegistrationError` entries), `docs/performance.md`,
      README Status section, `CHANGELOG.md` (0.0.7-beta)

## Phase 20 — Production hardening for framework use (1.0.0-rc1)

User goal: make inito production-ready for drop-in use in any Python project
(Django, FastAPI, Sanic, ...). This phase is a hardening/verification pass, not
new core features — plus one opt-in builder enhancement surfaced by the interop
work. Cut as `1.0.0-rc1` (release candidate) ahead of a stable `1.0.0`,
promoting the PyPI status from Alpha to Production/Stable.

- [x] **Codegen robustness/security fix**: audited every generator for
      untrusted-string interpolation into `exec()`'d source. Only `ReprGenerator`
      baked the owning class's `__name__` into the source text; a class created
      dynamically with an unusual `__name__` (framework metaclass via
      `type(name, ...)`) could crash decoration or, with a hostile name, inject
      statements into the function body. Fixed by passing the name through the
      generated function's globals (`_cls_name`) instead of the source string —
      zero behaviour change, names now render verbatim. Regression test added in
      `tests/generators/test_repr_generator.py`. All `qualified_name` uses
      elsewhere are only passed as the `qualname` *argument* to `build_function`
      (compile-filename label + `__qualname__` attribute), never compiled as
      code — confirmed safe.
- [x] **Python 3.14 support (PEP 649/749 lazy annotations)**: `collect_ordered_field_names`
      read `klass.__dict__.get("__annotations__")` directly, which misses fields
      under 3.14's lazy annotation evaluation (the key may be unmaterialised).
      Added `_own_annotation_names`, which uses `annotationlib.get_annotations`
      with the forward-reference format on 3.14+ (names without evaluating any
      value) and the `__dict__` read on <3.14. Full suite verified green on a
      throwaway 3.14 venv. Added 3.14 to the CI matrix and package classifiers.
- [x] **`@Builder(use_init=True)`**: opt-in build mode constructing via the
      class's own `__init__` instead of the default `__new__`+`object.__setattr__`
      bypass, so a validating framework model or hand-written constructor runs.
      The builder becomes a kwargs accumulator (only set fields passed;
      constructor owns defaults/required errors). Default behaviour unchanged.
      New `BuilderOptions.use_init`; mypy plugin untouched (the option doesn't
      change the synthesized Builder type). Unit tests in
      `tests/decorators/test_builder.py`.
- [x] **Framework interop test matrix** (`tests/integration/test_framework_interop.py`,
      importorskip-guarded): Pydantic v2 (additive decorators + `use_init`
      validation + documented default-bypass), SQLAlchemy 2.0 declarative
      (`use_init` + instrumentation + repr), Django (additive decorators in a
      configured process), custom-metaclass attachment, and async DI (concurrent
      `@Inject` resolution stability + explicit-arg precedence). New `interop`
      optional-dependency group; dedicated CI `interop` job on 3.12 (kept out of
      the main matrix since no single framework version spans 3.9–3.14).
- [x] **Security posture**: `SECURITY.md` (private disclosure process) + a
      `docs/security.md` page explaining the single decoration-time `exec()`
      site, that no user *values* reach compiled source, and the zero-dependency/
      no-I/O/no-monkeypatch stance.
- [x] **Docs**: new `docs/frameworks.md` (framework + async-DI usage guide),
      `use_init` documented on `docs/decorators/builder.md`, both new pages wired
      into the User Guide navigation; docs build clean under `-W`.
- [x] Published `1.0.0-rc1` to PyPI (status promoted Alpha → Production/Stable).

## Phase 21 — DI cold-resolution optimization (1.0.0-rc2)
- [x] Faster cold dependency-graph resolution (~900ns → ~700ns for a 3-level
      graph), warm path unchanged, by keeping inito's "reflect once" rule: each
      dependency's autowire type (Optional-unwrapped) is computed once at
      `@Service` registration and stored on `Dependency` (was re-derived via
      `typing.get_origin`/`get_args` on every `get()`); each singleton's
      construction lock is created at registration, so the cold path reads it
      with a plain dict lookup instead of guarding a lazily-built lock table.
- [x] Published `1.0.0-rc2` to PyPI; CI matrix + interop job green.

## Phase 22 — First-class Pydantic v2 support (1.0.0-rc3)
- [x] `reflection/introspection.py`: `is_pydantic_model` (duck-typed on
      `model_fields` + `__pydantic_validator__`; no pydantic import, zero-dep
      preserved) and a shared `reject_pydantic_target` guard.
- [x] `metadata/extractor.py`: `_fields_from_pydantic` reads defaults/required
      from `model_fields` (Pydantic keeps defaults there, not as class
      attributes), so a Pydantic-defaulted field is correctly optional.
- [x] `@Builder` auto-detects a Pydantic model and constructs through its
      validating `__init__` (implicit `use_init`); `_render_init_source` is now
      `use_init`-aware (leaves every field `_unset` so the target constructor
      owns all defaults, keeping `__pydantic_fields_set__` accurate).
- [x] Constructor-generating decorators (`@Data`/`@Value`/`@AllArgsConstructor`/
      `@NoArgsConstructor`/`@RequiredArgsConstructor`) raise
      `DecoratorConfigurationError` on a Pydantic model instead of silently
      overwriting its validating `__init__` (fail-loud, guard runs before any
      class mutation).
- [x] Tests: dep-free unit tests for detection/extraction/builder (duck-typed
      fakes, run on the full 3.9–3.14 matrix) + real-Pydantic interop tests in
      the `interop` CI job; full suite green, 97% coverage. Docs: new Pydantic
      section in `docs/frameworks.md`.
- [ ] Promote `1.0.0-rc3` → `1.0.0` after the RC soak (drop the suffix, new
      CHANGELOG entry, tag `v1.0.0`).
