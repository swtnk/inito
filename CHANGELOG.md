# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1-beta] - 2026-07-01

### Added
- Core metadata/reflection/code-generation engine: decoration-time-only
  field metadata extraction, an `exec()`-based method-generation utility,
  a shared dual-mode (`@dec`/`@dec(...)`) decorator factory, and a
  generator registry for capability-based reuse across decorators.
- `@Data`: constructor, `__repr__`, `__eq__`, `__hash__`, and
  `get_`/`set_` accessors for every declared field.
- `@Getter`, `@Setter`: accessors only.
- `@NoArgsConstructor`: no-argument constructor using field defaults.
- `@AllArgsConstructor`, `@RequiredArgsConstructor`: constructor-only
  decorators accepting every field or only required fields, respectively.
- `@Builder`/`builder`: a fluent, chainable builder (`.builder()...build()`)
  with `to_builder()` support (`to_builder=True`), `setter_prefix`, and
  `build_method_name` options. Works standalone on plain classes and
  composes with `@dataclass`.
- `@ToString`: `__repr__` only.
- `@EqualsAndHashCode`: `__eq__`/`__hash__` only.
- Full test suite (176 tests, 100% line+branch coverage), a
  pytest-benchmark/pyperf/tracemalloc/import-time benchmark suite, and
  Sphinx + Furo documentation (installation, quickstart, API reference,
  examples, migration guide, performance report, FAQ, troubleshooting).
- GitHub Actions CI (lint/format/typecheck/test/build across Python
  3.9-3.13) and a tag-triggered PyPI trusted-publishing release workflow.

### Known limitations
- Static type checkers (mypy/pyright) don't see generated members without
  a dedicated plugin (tracked for a future release).
- Stacking any constructor-generating decorator with
  `@dataclass(frozen=True)` raises `FrozenInstanceError` (expected, not a
  bug — see the README/troubleshooting docs).
- Self-referential forward references (e.g. `next: Node`) aren't supported,
  since annotations resolve eagerly at decoration time.
