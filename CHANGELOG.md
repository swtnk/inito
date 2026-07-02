# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.9-beta] - 2026-07-02

### Fixed
- `@Service`/`@Singleton` now correctly compose with `@RequiredArgsConstructor`,
  `@AllArgsConstructor`, `@Data`, and `@NoArgsConstructor`. A user-reported
  bug showed `@Service @RequiredArgsConstructor class UserService: helper:
  Helper` raising `DependencyRegistrationError: ... has no type annotation`
  even though `helper: Helper` is a perfectly normal field annotation —
  these decorators' generated `__init__` source carries no annotations at
  all (they only ever needed parameter *names* for their own codegen), so
  `resolve_constructor_dependencies` couldn't see a type for `helper` by
  inspecting `__init__` alone. It now falls back to the `ClassMetadata`
  that decorator already cached on the class at its own decoration time
  (reusing, not re-deriving, that reflection) whenever `__init__` itself
  has no annotation for a given parameter name.

## [0.0.8-beta] - 2026-07-02

### Fixed
- `@Value` and `@Data(frozen=True)` are now **genuinely immutable**, not
  just setter-free. A user-reported bug showed direct attribute assignment
  (`person.name = "Bob"`) silently succeeding on a `@Value`-decorated class
  built via `@Builder` — previously, real immutability only existed if you
  additionally stacked a real `@dataclass(frozen=True)` underneath, which
  wasn't obvious and didn't match Lombok's `@Value` contract (unconditional
  immutability, no extra annotation needed). Both decorators now attach a
  generated `__setattr__`/`__delattr__` pair (new `immutable` generator
  capability) that unconditionally raises `dataclasses.FrozenInstanceError`
  after construction — every inito constructor (`@Data`'s `__init__`,
  `@Builder`'s `build()`, `@NoArgsConstructor`/`@RequiredArgsConstructor`)
  already assigns fields via `object.__setattr__`, so this required no
  change to any of them and adds no construction-time or attribute-read
  overhead. `@dataclass(frozen=True)` stacking still works (doubly frozen)
  but is no longer required for either decorator.

## [0.0.7-beta] - 2026-07-02

### Added
- A dependency-injection subsystem: `@Service`/`@Component` (registers a
  class's constructor dependency types into a `Container` at decoration
  time, without instantiating or mutating anything — the class stays an
  ordinary, directly-constructible Python class), `@Singleton` (a
  standalone decorator, sugar for `@Service(scope=Scope.SINGLETON)`), and
  `@Inject` (wraps a function so its type-annotated, unfilled parameters
  are resolved from a container on every call). `Container.get(cls)`
  lazily resolves and builds the dependency graph bottom-up on first
  request, caching singleton-scoped instances; a constructor parameter is
  autowired only if its type is itself registered, otherwise its default
  value (if any) applies, otherwise resolution raises
  `UnresolvableDependencyError`. New `DependencyRegistrationError`,
  `UnresolvableDependencyError`, and `CircularDependencyError` exception
  types. This is the library's first process-wide mutable state — every
  prior decorator was purely per-class. `Container.get` is a plain
  generic method (`type[T] -> T`), so it's correctly typed under both
  mypy and pyright natively, with no plugin or `.pyi` stub needed.
  `@Inject` is the one decorator in this library with a real, documented
  per-call cost (see `docs/quickstart.md`/`docs/performance.md`) — every
  other generated member remains zero-overhead after construction, which
  benchmarks confirm holds for DI-resolved instances too. Pulled forward
  from `inito.md`'s Future Features list, following `@Value` in 0.0.6-beta.

## [0.0.6-beta] - 2026-07-02

### Added
- `@Value`/`value`: an immutable-style data class decorator — constructor,
  `__repr__`, `__eq__`, `__hash__`, and `get_<field>()` accessors, but
  *never* `set_<field>(value)` (unlike `@Data`, which only omits setters
  when `frozen=True` is passed explicitly). Stack with
  `@dataclass(frozen=True)` for genuine attribute-write immutability.
  Reuses the same constructor/repr/eq/hash/getter generators `@Data` and
  `@AllArgsConstructor` already use — no new generator was needed. Comes
  with mypy plugin support and a `dataclass_transform`-marked `.pyi` stub
  for pyright, matching `@Data`/`@AllArgsConstructor`'s existing typing
  support. Pulled forward from `inito.md`'s Future Features list ahead of
  the rest of that list (including the `@Service`/`@Inject`/`@Singleton`
  dependency-injection work), since it's a thin composition of existing
  capabilities rather than a new subsystem.

## [0.0.5-beta] - 2026-07-02

### Fixed
- Self-referential forward references (e.g. a linked-list `next: Node`) now
  resolve correctly instead of raising `AnnotationResolutionError`.
  `resolve_type_hints` temporarily seeds the class's own module namespace
  with the class itself just before resolution (restored immediately after
  in a `finally`), only when that name isn't already bound to something
  else. This is a decoration-time-only change — no added per-instance or
  per-call cost, and genuinely unresolvable names still correctly raise.

## [0.0.4-beta] - 2026-07-02

### Fixed
- Generated constructors (`@Data`'s `__init__`, `@Builder`'s `build()`,
  `@AllArgsConstructor`, `@NoArgsConstructor`, `@RequiredArgsConstructor`)
  now assign fields via `object.__setattr__` instead of plain attribute
  assignment, so they work correctly when stacked with
  `@dataclass(frozen=True)` in either order — matching how a real frozen
  dataclass's own `__init__` bypasses its blocking `__setattr__` for
  initial construction. Previously this raised `FrozenInstanceError` on
  construction itself, which 0.0.3-beta's docs incorrectly described as
  "expected, not a bug" until a real usage report prompted reconsidering
  it. Setters remain plain assignment, so post-construction mutation on a
  frozen dataclass still correctly fails.

## [0.0.3-beta] - 2026-07-01

### Added
- `decorators/data.pyi` and `decorators/all_args_constructor.pyi`: `.pyi`
  stubs marking `@Data`/`@AllArgsConstructor` with standard
  `typing.dataclass_transform` (PEP 681), so **pyright** (which has no
  plugin mechanism) also gets a correctly-typed constructor for these two
  decorators — no inito-specific setup needed beyond having the package
  installed. Deliberately not applied to `@NoArgsConstructor`/
  `@RequiredArgsConstructor`: verified their real constructor signatures
  can't be expressed by `dataclass_transform` without pyright silently
  accepting calls the runtime would reject.

## [0.0.2-beta] - 2026-07-01

### Added
- A mypy plugin (`inito.typing.mypy_plugin`) synthesizing every generated
  member's real type: `__init__`'s signature, `get_x`/`set_x` accessors, and
  the full `@Builder` fluent chain (`Builder`, `builder()`, `to_builder()`).
  Enable via `[tool.mypy] plugins = ["inito.typing.mypy_plugin"]`. Closes the
  mypy half of the "static type checkers don't see generated members" known
  limitation from 0.0.1-beta; pyright has no equivalent plugin mechanism and
  remains a documented gap.

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
