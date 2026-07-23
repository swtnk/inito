# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-07-21

Safety fixes to the data-model semantics so inito upholds the guarantees a
`dataclasses`/`attrs` replacement is expected to provide. Some of these change
behavior that `1.0.0` accepted silently; each replaces a silent footgun with a
clear error or the correct result.

### Added

- **`field()`** — declare a field's default explicitly, the inito-native
  equivalent of `dataclasses.field`: `items: list = field(default_factory=list)`
  builds a fresh object per instance, and `field(default=...)` sets a plain
  default. Recognized by the mypy plugin and (via PEP 681 `field_specifiers`) by
  pyright, so the annotated field type still checks. New `field` export.
- **`__post_init__` hook.** If a class defines `__post_init__(self)`, every
  generated constructor calls it after assigning the fields — the place to
  enforce invariants, exactly like `dataclasses`. A frozen class sets derived
  fields from the hook via `object.__setattr__`. The builder's direct-build path
  calls it too, so a builder-constructed instance runs the same invariants.
- **`@Data(accessors=...)`** — choose the accessor style: `"lombok"` (default,
  `get_x`/`set_x`), `"attr"` (none — the attribute *is* the accessor, the
  Pythonic style), or `"both"` (alias of `"lombok"`). Honored by the mypy plugin,
  so `accessors="attr"` also drops `get_`/`set_` from what the type-checker sees.
- **`slots=True`** on `@Data`/`@Value` — recreate the class with `__slots__` for
  a smaller per-instance footprint and no accidental attributes, the way `attrs`
  does. Field defaults, getters/setters, `__post_init__`, `super()` in your
  methods, and `weakref` all keep working; the mypy plugin models the slots so an
  undeclared attribute is a type error too. (Put `@Builder` outside
  `@Data(slots=True)` when stacking, so the builder targets the rebuilt class.)
- **`@Value(freeze_collections=True)`** — store a mutable collection field as an
  immutable one at construction (`list`→`tuple`, `set`→`frozenset`,
  `dict`→read-only `MappingProxyType`), hardening `@Value`'s shallow freeze. A
  `list`/`set` field then also becomes hashable. Shallow by design; the declared
  annotation is unchanged, so treat the stored value as read-only.

- **Readable tracebacks through generated code.** Each generated method's source
  is registered with `linecache`, so a traceback that passes through a generated
  `__init__`/`__eq__`/`__post_init__` frame shows the real source line instead of
  a blank `<inito:...>` frame.

### Changed (typing)

- **Stronger zero-config pyright support.** `@Value` now carries a
  `dataclass_transform` stub (like `@Data`/`@AllArgsConstructor`), and all three
  declare `field` as a PEP 681 `field_specifier`, so the constructor, the fields,
  and `field(default_factory=...)` type-check under pyright with no stubgen. The
  Pythonic `accessors="attr"` style is fully covered zero-config; Lombok
  accessors and `@Builder` still need `inito-stubgen` for pyright.

### Fixed

- **Mutable default values are no longer silently shared across instances.** A
  mutable literal default (`items: list = []`) now raises
  `InvalidFieldDefinitionError` at decoration time — as `dataclasses` and `attrs`
  do — pointing to `field(default_factory=...)`. Previously every instance shared
  one object.
- **A field name that is not a valid identifier, is a keyword, or collides with
  inito's generated code** now raises `InvalidFieldDefinitionError` instead of
  producing a miscompiled method. All codegen-internal globals are namespaced
  under a reserved `_inito_` prefix, and field names using that prefix are
  rejected, so a field can never shadow an internal helper (e.g. a field named
  `_setattr` no longer breaks a frozen constructor).
- **Hand-written methods are no longer overwritten.** A `__repr__`, `__eq__`,
  `__init__`, etc. that you define in the class body is left untouched;
  inito only generates the members you didn't write. (Methods synthesized by a
  stacked `@dataclass` are still taken over, as before.)

### Changed (behavior)

- **A mutable `@Data` class is now unhashable** (`__hash__` is `None`), matching
  `dataclasses(eq=True, frozen=False)`, so a mutated instance can no longer break
  its own `set`/`dict` membership. Use `@Data(frozen=True)` or `@Value` for a
  hashable value type; a `@Data` stacked on a frozen dataclass stays hashable.
- **Constructor parameters keep declaration order.** The generated `__init__` no
  longer reorders required fields ahead of defaulted ones; a required field
  declared after a defaulted one now raises `InvalidFieldDefinitionError` (as
  `dataclasses` does) instead of silently permuting positional arguments. The
  mypy plugin reports the same case.

## [1.0.0] - 2026-07-21

First stable release. The API is now considered stable and follows Semantic
Versioning: breaking changes will require a major-version bump.

No source changes since `1.0.0-rc8` — this promotes the release-candidate series
(`rc1`–`rc8`) to a stable guarantee. The complete, itemized history of everything
that shipped across the candidates is preserved in the entries below.

### Highlights

- Zero-runtime-dependency boilerplate decorators: `@Data`, `@Value`, `@Builder`,
  `@Getter`/`@Setter`, `@ToString`, `@EqualsAndHashCode`, and the constructor
  family (`@NoArgsConstructor`/`@AllArgsConstructor`/`@RequiredArgsConstructor`).
- Annotation-native dependency injection: `Container`, `@Singleton`/`@Service`/
  `@Component`, `Scope` (`SINGLETON`/`TRANSIENT`/`THREAD_LOCAL`/`SCOPED`),
  `Qualifier`, `Factory[T]`, `@Resource` lifecycle management, full async
  resolution, and FastAPI `Injected[T]`.
- `@Config` environment/settings loading and `@Jsonize` serialization.
- Static-typing support across the surface: a mypy plugin, PEP 681
  `dataclass_transform` stubs for pyright, and the `inito-stubgen` CLI.

## [1.0.0-rc8] - 2026-07-13

### Added

- **`@Jsonize` — `to_dict()` / `to_json()` serialization.** Generates a
  `to_dict(self) -> dict[str, Any]` and `to_json(self, **kwargs) -> str` over a
  class's declared fields, coercing the types `json.dumps` can't handle:
  `datetime`/`date`/`time` (ISO 8601), `UUID`, `Decimal`, `Enum` (by value),
  `bytes`/`bytearray` (base64), `os.PathLike`, mappings, sequences/sets, and
  nested `@Jsonize` objects; anything else is stringified. `to_json` forwards its
  keyword arguments to `json.dumps`. Handy for returning inito objects from a
  FastAPI handler (`return obj.to_dict()`), logging, and storage. Built the inito
  way — a new `json` capability + generator + thin decorator — with mypy-plugin
  and `inito-stubgen` support, so `mypy --strict` and pyright both see the two
  methods. New `Jsonize`/`jsonize`/`JsonizeOptions` exports.

### Changed (performance — no behavior change)

- **`@Inject` now generates a wrapper specialized to the function's own
  signature** (for ordinary signatures — `*args`/`**kwargs`/positional-only fall
  back to the generic wrapper), skipping the per-call `*args`/`**kwargs` packing
  and the per-parameter loop. ~56% faster on the resolve path (≈130 ns → ≈57 ns
  on the benchmark machine), within a few ns of a plain call plus one
  `container.get()`. All existing `@Inject` behaviors are preserved; generated
  helper names are namespaced so a parameter can never shadow them.

## [1.0.0-rc7] - 2026-07-13

### Changed (performance — no behavior change)

- **`__eq__` is now an allocation-free field-by-field `and`-chain** (`self.a ==
  other.a and ...`) instead of comparing two freshly built tuples. It allocates
  nothing per call and short-circuits on the first differing field — the same
  code you'd write by hand — so it is faster than the tuple form `dataclasses`
  emits (measured ~20% on the comparison). Semantics are unchanged.
- **Single-field classes hash the field directly** (`hash(self.a)`) rather than
  wrapping it in a one-element tuple, dropping a per-call allocation (~30% on the
  hash). Multi-field hashing still hashes a tuple of every field. Hash/eq
  consistency is preserved.
- **`@Inject`'s per-call resolution folds the former `is_registered` + `get` pair
  into a single container traversal** (`_resolve_optional`: override → warm
  singleton → registration), bound once at decoration — so each unfilled,
  registered parameter costs one lookup instead of two (~15% on the resolve
  step). Overrides and scopes are still honored per call.

## [1.0.0-rc6] - 2026-07-13

### Added

- **`Scope.SCOPED` + `container.scope()` — per-scope lifetimes.** A `contextvars`
  -based scope (usable as `with container.scope():` or `async with`) caches one
  instance of a `Scope.SCOPED` service per scope — a request, task, or unit of
  work — and tears down any scoped `@Resource` (LIFO) when the scope exits.
  Scopes nest (innermost wins). Resolving a scoped service with no active scope
  raises the new `ScopeError`. `@Resource` may now be singleton- **or**
  scope-scoped.
- **Full async resolution — `await container.aget(cls)`.** `aget` now resolves the
  **entire** dependency graph asynchronously, awaiting an async `@Resource`
  generator provider *anywhere* in it (not only at the top), so an async resource
  can be an ordinary constructor dependency. Sync `get()` is unchanged.
- **FastAPI `Injected[T]`.** `Injected[T]` (or `Injected(T, container=...)`) is a
  FastAPI dependency that resolves `T` from the container per request, inside a
  per-request `container.scope()` — so a scoped `@Resource` opens and closes with
  the request. FastAPI stays an **optional** dependency (imported lazily, never at
  runtime); using `Injected` without it raises the new `FrameworkIntegrationError`.

## [1.0.0-rc5] - 2026-07-12

### Added

- **`@Resource` — resource lifecycle with ordered teardown.** Mark a
  `@Service`/`@Singleton` **class** (torn down by its `close()`/`aclose()` method,
  name configurable, or its `__enter__`/`__exit__` context-manager protocol) or a
  **generator-provider function** (`yield` the resource, then clean up after the
  yield; its parameters are autowired, and it registers a provider keyed by the
  yielded type). The `Container` builds each resource lazily and closes them in
  reverse construction order (LIFO) at `shutdown_resources()` or when a
  `with container:` block exits. **Async** resources (an `async` close method or an
  `async def` generator) are awaited by `await container.ashutdown_resources()` /
  `async with container`, and an async generator provider is built with the new
  `await container.aget(cls)`. Teardown is best-effort — every resource is closed
  even if one raises, with failures aggregated into one new `ResourceTeardownError`.
  Zero-dependency and reflect-once: each resource's teardown strategy is determined
  once, at decoration/registration time.

- **`Factory[T]` — on-demand construction with call-time arguments.** Inject a
  `Factory[T]` constructor parameter and call it to build a **fresh** `T` per
  call: registered-typed parameters are autowired from the container, call-time
  keyword arguments supply (and override) the rest, and anything left falls to
  the target's own default. The target need not itself be registered (a
  *prototype* factory), and because a factory is lazy a `Factory[B]` parameter
  breaks an otherwise-circular graph. `Factory` is both the annotation and the
  static type — `mypy` and pyright infer `make(...) -> T` with no plugin or
  stub. Zero-dependency and reflect-once: the target's constructor plan is
  inspected once, when the factory is injected.

## [1.0.0-rc4] - 2026-07-03

### Added

- **Dependency injection — new capabilities (all zero-dependency,
  annotation-native, reflect-once):**
  - **Test overrides.** `Container.override(cls, instance)`,
    `override_factory(cls, factory)`, `clear_override`/`clear_overrides`, and a
    `with container.overrides({T: obj}):` context manager. An override wins over
    the singleton cache and needs no prior registration; `reset()` clears
    overrides too. The warm `get()` path is unregressed.
  - **`Scope.THREAD_LOCAL`** — one instance per thread.
  - **`@Config`** — load a class's fields from environment variables (with an
    optional prefix), coerced to the annotated type; register it as a `@Service`
    to autowire it by type. New `ConfigResolutionError`.
  - **Qualifiers for multiple implementations** — `@Service(qualifier="name",
    primary=...)` + `typing.Annotated[Repo, Qualifier("name")]` (or a bare
    string). A bare interface resolves the sole or `primary` implementation;
    several with no primary raise `AmbiguousDependencyError`. New `Qualifier`.
- **`inito-stubgen`** — a stub generator that emits `.pyi` files exposing every
  generated member to **pyright / Pylance** (accessors, the `@Builder` chain,
  and all constructor signatures), closing the long-standing pyright gap. Opt-in
  and dev-time only (`pip install inito[stubgen]`); inito's runtime stays
  zero-dependency.
- **Framework examples gallery** (`examples/di/`) — runnable, override-tested
  apps wiring inito's DI into FastAPI, Django, Sanic, aiohttp, Redis, Valkey,
  boto3, RabbitMQ, and env-config, each with a smoke test and a dedicated CI job.

### Documentation

- Reworked the README into a comprehensive PyPI landing page: a declarative
  intro (no longer led by "Lombok"), a table of contents, a section per decorator
  with options, a full dependency-injection walkthrough (including a plain-English
  "what a Container is"), inline framework examples, type-checking, performance,
  design, and an exceptions reference.
- Documented every DI 2.0 feature on the docs site (thread-local scope,
  qualifiers, configuration injection, overrides) and added a `@Config`
  decorator page; scrubbed "Lombok" from the docs, keeping a single factual FAQ
  note.

## [1.0.0-rc3] - 2026-07-03

### Added
- **First-class Pydantic v2 support** — InitO now detects a Pydantic model (by
  duck-typing; it still never imports Pydantic, so the zero-runtime-dependency
  promise holds) and adapts:
  - **`@Builder` just works on a Pydantic model.** Bare `@Builder` constructs
    through Pydantic's validating `__init__` automatically (no `use_init=True`
    needed) and reads each field's default and required-ness from the model, so
    a Pydantic-defaulted field is optional in the builder instead of being
    wrongly reported as required. The built instance is fully valid
    (`__pydantic_fields_set__` reflects exactly the fields you set, and passing
    a bad value raises `pydantic.ValidationError`).
  - The additive decorators (`@Getter`/`@Setter`/`@ToString`/
    `@EqualsAndHashCode`) compose with Pydantic models as before.

### Changed
- **Constructor-generating decorators now fail loud on a Pydantic model.**
  `@Data`, `@Value`, `@AllArgsConstructor`, `@NoArgsConstructor`, and
  `@RequiredArgsConstructor` would overwrite Pydantic's validating `__init__`
  and silently disable validation, so they now raise
  `DecoratorConfigurationError` at decoration time, pointing at `@Builder` plus
  the additive decorators. (Previously this was a silent footgun.)
- `@Builder(use_init=True)` no longer pre-populates inito-visible field defaults
  into the builder; only the fields the caller actually sets are passed to the
  constructor, so the target constructor's own defaults always apply. This makes
  the Pydantic/framework behavior consistent and keeps `__pydantic_fields_set__`
  accurate.

## [1.0.0-rc2] - 2026-07-03

### Changed (performance — no behavior change)
- **Faster cold dependency-graph resolution** (~900ns → ~700ns for a 3-level
  graph; warm `container.get()` and resolved-instance attribute access are
  unchanged). Two decoration-time moves, both keeping inito's "reflect once"
  rule: each dependency's autowire type (its `Optional[...]`/`X | None` wrapper
  stripped) is now computed once at `@Service` registration and stored on
  `Dependency`, instead of calling `typing.get_origin`/`get_args` on every
  `get()`; and each singleton's construction lock is created at registration,
  so the cold path reads it with a plain dict lookup rather than guarding a
  lazily-built lock table. Thread-safety and all resolution semantics are
  identical.

### Documentation / CI
- Docs are now published to the `gh-pages` branch (built by CI, served via
  Pages' "Deploy from a branch" mode) instead of the Pages deployment API,
  which had wedged on a stuck deployment; this path can't hit that failure.

## [1.0.0-rc1] - 2026-07-02

First release candidate for a stable **1.0.0**. All of `inito.md`'s Initial
Features plus `@Value` and dependency injection are complete, and this release
adds a production-hardening pass: framework interoperability, Python 3.14
support, a code-generation robustness fix, and an opt-in framework-aware
builder. The package's PyPI status is promoted from Alpha to
**Production/Stable**.

### Added
- **`@Builder(use_init=True)`** — an opt-in build mode that constructs through
  the class's own `__init__` instead of bypassing it, so a validating framework
  model (Pydantic, SQLAlchemy, Django) or a hand-written constructor runs its
  validation/instrumentation. In this mode `build()` passes only the fields you
  actually set, deferring defaults and required-argument errors to the
  constructor. The default (fast, `__init__`-bypassing) behaviour is unchanged.
- **Python 3.14 support.** Added 3.14 to the CI matrix and the package
  classifiers.
- **Framework-interoperability test suite** (`tests/integration/test_framework_interop.py`)
  verifying InitO composed with Pydantic v2, SQLAlchemy 2.0 declarative, Django,
  a custom metaclass, and async dependency-injection resolution. Frameworks are
  optional dev extras (`.[interop]`) and run in a dedicated CI job.
- **`SECURITY.md`** with a private vulnerability-disclosure process, and a new
  **Security & code generation** documentation page explaining how and when
  `exec()` runs and why no user input reaches the compiled source.
- **Using InitO with your framework** documentation page (Django/FastAPI/Sanic/
  Pydantic/SQLAlchemy, async DI, and the additive-vs-constructor decorator
  guidance).

### Fixed
- **Robust code generation for dynamically-named classes.** `__repr__` no longer
  interpolates the owning class's `__name__` into the generated source; the name
  is passed through the function's globals instead. A class created dynamically
  with an unusual `__name__` (e.g. by a framework metaclass via `type(name,
  ...)`) previously could crash decoration or, with a hostile name, inject
  statements into the generated function body. Names now render verbatim with no
  crash or injection.
- **Python 3.14 lazy annotations (PEP 649/749).** Field discovery no longer reads
  `__annotations__` directly from a class's `__dict__` (which may be unmaterialised
  under 3.14's lazy evaluation); it uses `annotationlib` with the forward-reference
  format on 3.14+, retrieving field names without evaluating any annotation value.

### Changed
- PyPI **Development Status** classifier promoted from `3 - Alpha` to
  `5 - Production/Stable`.

### Documentation
- The Sphinx docs are now published to GitHub Pages and served at
  <https://swetanksubham.com/inito/> (auto-deployed on every push to `main`
  via a new `docs.yml` workflow). Repointed the PyPI `Documentation` project
  URL and the README's doc links/badge to the hosted site.
- Switched the docs theme from Furo to the **PyData Sphinx Theme** with
  `sphinx-design`: a top navbar with search, light/dark toggle, and
  GitHub/PyPI links; a card-grid landing page; and a right-hand
  on-this-page sidebar.
- Restructured the docs into two navbar sections — **User Guide** and
  **API reference** — each with its own grouped "Section Navigation". The
  User Guide groups the decorator/DI/recipe pages under captions (Getting
  started · Decorators · Dependency injection · Recipes and guides · Help);
  the API reference is split into Decorators, Dependency injection, and
  Exceptions pages. The docs now brand the project as **InitO** (the
  installable package remains `inito`).

## [0.0.12-beta] - 2026-07-02

### Documentation
- Reworked the README (PyPI/GitHub) with badges, a "decorators at a glance"
  table, an inline dependency-injection example, and absolute links that
  resolve on PyPI.
- Restructured the Sphinx docs into grouped, captioned navigation (Getting
  started · Decorators · Dependency injection · Guides · Reference) with a
  **dedicated page per decorator** — `@Data`, `@Value`, accessors,
  `@ToString`, `@EqualsAndHashCode`, a grouped **Constructors** page
  (`@NoArgsConstructor`/`@AllArgsConstructor`/`@RequiredArgsConstructor`),
  `@Builder`, and a full **Dependency injection** page. Each page opens with
  the specific problem it solves, then usage, options, and gotchas. Added a
  **Concepts** page ("the problem inito solves") and a **Recipes** page of
  real-world combined patterns; every recipe block is executed by the test
  suite (`tests/integration/test_recipes_run.py`) so it can't drift.

### Fixed
- **Reverted a performance regression from 0.0.11-beta.** That release
  assigned constructor fields via `self.__dict__["x"] = x`, which is a hair
  faster to construct but breaks CPython's key-sharing instance dict
  (PEP 412) — silently regressing *every* attribute read (+~40%) and
  `__eq__`/`__hash__`/`__repr__` (+~80%), which are far hotter than
  construction. Constructors now use a plain `self.x = x` for ordinary
  classes (fastest, and key-sharing-friendly) and a once-bound
  `object.__setattr__` only for immutable classes (`@Value`,
  `@Data(frozen=True)`, or a class stacked on `@dataclass(frozen=True)`),
  which also preserves key-sharing. Result: inito is now at handwritten/
  dataclasses parity on construction **and** reads **and** eq/hash/repr.

### Changed (performance — no behavior change)
- `Container.get()` now fast-paths a warm/cached singleton through a single
  dict lookup (ahead of the registration/scope/cycle checks and skipping
  `typing.cast`), ~1.75x faster on the hottest DI call (~79ns → ~45ns).

### Removed / breaking
- Stacking `@dataclass(frozen=True)` **outermost** — i.e. applied *after*
  an inito constructor decorator (`@dataclass(frozen=True)` on top of
  `@Data`) — is no longer supported: construction raises
  `FrozenInstanceError`, because inito generates its `self.x = x`
  constructor before the outer `@dataclass` installs its frozen
  `__setattr__` and can't detect it. This was previously made to work by
  using `object.__setattr__` for *every* class, which is what caused the
  read/eq/hash slowdown. Use the **innermost** order
  (`@Data` / `@dataclass(frozen=True)`), or `@Value` / `@Data(frozen=True)`
  (no stacking needed) — all of which keep full read performance.

## [0.0.11-beta] - 2026-07-02

### Changed (performance — no behavior change)
- Generated constructors (`@Data`, `@AllArgsConstructor`,
  `@RequiredArgsConstructor`, `@NoArgsConstructor`, `@Value`) and
  `@Builder`'s `build()` now assign fields via a direct
  `self.__dict__["x"] = x` write for ordinary classes instead of
  `object.__setattr__`. This is ~2x faster (construction went from ~2.5x
  handwritten to ~1.2-1.3x) and, because a `__dict__` write bypasses
  `__setattr__` entirely, it stays immutable-correct in every stacking
  order — `@Value`, `@Data(frozen=True)`, and `@dataclass(frozen=True)`
  (inner or outer) all keep working with no per-instance branching. Fully
  slotted classes (no instance `__dict__`) fall back to a once-bound
  `object.__setattr__`. The previously-published construction benchmark
  had never been re-measured after `object.__setattr__` was introduced in
  0.0.4-beta and understated the cost; `docs/performance.md` is corrected.
- `@Inject` no longer calls `inspect.Signature.bind_partial()` on every
  call. Each parameter's name, positional index, and resolved type are now
  computed once at decoration time; the per-call path only checks which
  arguments the caller already supplied. Measured ~4x faster (~830ns →
  ~200ns per call), identical behavior. All signature/type-hint reflection
  stays at decoration time, matching the rest of the library.

### Fixed
- The DI container now resolves a service's dependencies *before* taking
  that service's construction lock, so no thread ever holds two singleton
  locks at once. This eliminates a latent deadlock where two threads
  resolving a cyclic graph from opposite ends could hang instead of raising
  `CircularDependencyError`; concurrent resolution of a cycle now raises
  cleanly. Single-construction-under-contention and the lock-free warm path
  are both preserved.

## [0.0.10-beta] - 2026-07-02

### Fixed
- `@Singleton`/`Container` singleton resolution is now thread-safe. A user
  asked whether it was thread- and process-safe; verified empirically with
  real `threading`/`multiprocessing` reproductions that concurrent
  first-access from multiple threads was **not** safe — 20 threads racing
  a cold `get()` produced 20 separate constructions and 20 distinct
  "singleton" instances, a genuine check-then-act race with no lock
  (`TASKS.md` Phase 19 had originally documented "no thread-locking in
  v1" as a deliberate scope decision). Fixed via double-checked locking: a
  lazily-created lock per registered class, acquired only on the cold
  path — the already-benchmarked warm/cached `get()` path is completely
  unaffected (confirmed via `benchmarks/test_di_benchmark.py`, no
  regression on the warm-cache numbers). Uses `threading` from the
  standard library only, no new dependency. As expected (and confirmed
  via a real `multiprocessing` reproduction, not something to fix), a
  `Container` remains process-local — no in-memory Python object can be
  shared across OS processes without external state.

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
