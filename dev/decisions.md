# Decision log (ADR-lite)

Newest first. One entry per non-obvious decision: what, why, and any tradeoff.
Keep entries short — this is for fast re-grounding, not prose.

## DI 2.0: zero-dep core, framework paths optional
Every DI-2.0 capability must work with no third-party dependency. Pydantic,
YAML, and FastAPI are optional, duck-typed paths — never unconditionally
imported. **Why:** the zero-runtime-dependency, install-anywhere property is
inito's core differentiator (vs. `dependency-injector`). Config injection ships
a plain `@Config` env/YAML mapper AND supports Pydantic `BaseSettings` when
present.

## DI 2.0: annotation-native, not markers/providers
Capabilities are driven by type annotations + decorators (e.g.
`Annotated[T, qualifier]`), not `Provide[]` markers or explicit provider
objects. **Tradeoff:** less see-it-all-in-one-file explicitness than
dependency-injector; accepted, matches inito's philosophy.

## dev/ is the durable, git-tracked source of truth
Harness plan/memory paths (`~/.claude/…`) can't be relocated, so `dev/` (tracked)
holds the roadmap, tasks, plan mirrors, and this log. **Why:** resumable at any
point on any clone; keeps the finished 602-line history off the hot context path.

## Cython/C: rejected for inito
Generated methods run at native Python speed (parity with handwritten) and are
not part of inito's compiled package, so Cython can't accelerate them; only the
DI container is compilable, and it isn't a bottleneck. Cost would be the
zero-dep/pure-Python/install-anywhere identity. **Decision:** stay pure Python.

## Pydantic v2: auto-detect for @Builder; guard constructor decorators
`@Builder` on a Pydantic model constructs through Pydantic's validating
`__init__` and reads defaults from `model_fields`; constructor-generating
decorators raise `DecoratorConfigurationError` (they'd overwrite validation).
Detection is duck-typed (`model_fields` + `__pydantic_validator__`), no import.

## Construction: `self.x = x`, `object.__setattr__` only when frozen
Plain assignment keeps CPython's key-sharing instance dict (PEP 412); a
`__dict__` subscript write breaks it and slows every read/eq/hash/repr. Frozen
classes use a once-bound `object.__setattr__`. **Tradeoff:** stacking
`@dataclass(frozen=True)` *outermost* is unsupported (use innermost / `@Value`).

## Release cadence: ship each increment as `1.0.0-rcN`
Kept in RC through the hardening/feature waves so the API can settle before a
stable `1.0.0`. Each phase is its own rc; promote to `1.0.0` after a clean soak.
