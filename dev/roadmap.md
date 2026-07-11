# DI 2.0 roadmap

**Goal:** cover the cases the `dependency-injector` framework solves, in inito's
own **zero-dependency, annotation-native** way — driven by type annotations and
decorators, not `Provide[]` markers or explicit provider/container definitions.

**Guardrails (non-negotiable):**
- Zero runtime dependencies; any framework (Pydantic, YAML, FastAPI) is optional
  and detected/duck-typed, never imported unconditionally.
- Reflect once at decoration/registration time; nothing re-inspects annotations
  per `get()`/call.
- Warm `get()` and generated-method speed must not regress.

## Capability → annotation-native design

| Capability (dependency-injector) | inito design | Phase |
|---|---|---|
| Test overriding | `container.override(T, obj)` / `with container.overrides({T: obj}):`; `get()` checks overrides first | 1 |
| Config injection (env/YAML/pydantic) | `@Config` class populated from env/YAML (zero-dep) **or** a Pydantic `BaseSettings`; autowired **by type** | 1 |
| Multiple impls / selection | `typing.Annotated[Repo, "postgres"]` + `@Service(qualifier="postgres")`; a `primary` default | 1 |
| Thread-local singleton | `Scope.THREAD_LOCAL` | 1 |
| Factory with call-time args | inject `Factory[Widget]`; inito autowires Widget's deps, caller passes the rest | 2 |
| Resource lifecycle (open/close) | `@Resource` on a context-manager/generator service; `with container:` / `shutdown_resources()`; sync + async | 3 |
| Async construction | `await container.aget(cls)` | 4 |
| Request/scoped lifetime | `Scope.SCOPED` + `async with container.scope() as s:` | 4 |
| Framework wiring (FastAPI/…) | `@Inject` (already async-safe) + an `Injected[T]` FastAPI `Depends` helper | 4 |

## Honest tensions (calibrated, not hidden)
- Resource teardown and request scope inherently need an imperative lifecycle
  boundary (`with container:` / enter-exit a scope). Annotations *mark* the
  resource; the boundary is still explicit — same as dependency-injector's own
  `init_resources()`/`shutdown_resources()`.
- Full annotation-magic trades away some of dependency-injector's
  see-it-all-in-one-file explicitness. Accepted, in line with inito's philosophy.

## Phases (value ÷ effort order)

- **Phase 1 — high-ROI, elegant:** test overriding · config injection (zero-dep
  `@Config` + optional Pydantic `BaseSettings`) · `Annotated[T, qualifier]` ·
  `Scope.THREAD_LOCAL`. Closes the gaps most real projects hit; all S–M effort.
- **Phase 2 — Factory[T]:** call-time args alongside injected deps.
- **Phase 3 — Resource lifecycle:** `@Resource`, container as (async) context
  manager, ordered teardown.
- **Phase 4 — Scopes + async + framework glue:** `Scope.SCOPED`,
  `container.scope()`, `await container.aget()`, FastAPI `Injected[T]`.

Each phase: design → `dev/plans/di2-phase-N.md`, implement (reusing
`attach_capability`/`make_decorator`, the existing `Container`), tests mirroring
`tests/`, docs, then ship as an `rc`.
