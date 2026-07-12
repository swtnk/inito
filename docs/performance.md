# Performance

`inito`'s core design constraint is that decoration-time work (reflection,
metadata extraction, code generation) happens exactly once, and generated
methods perform like handwritten ones — never worse, and never with
per-call or per-instance overhead. This page documents how that's measured
and what the numbers actually show.

## Methodology

Every comparison uses the same `Point`-shaped class (two required fields,
one defaulted) implemented four ways:

- **handwritten** — a manually written class, the baseline.
- **InitO** — the same class decorated with `@Data` (and `@Builder` where noted).
- **dataclass** — `@dataclasses.dataclass`.
- **attrs** — `@attrs.define` (slotted by default).

Two tools are used, per `inito.md`'s benchmarking requirements:

- **pytest-benchmark** (`benchmarks/test_*_benchmark.py`) — convenient for
  local/CI regression tracking across construction, attribute access,
  `__repr__`, `__eq__`, `__hash__`, decoration time, and `@Builder`'s fluent
  chain vs. a direct constructor call.
- **pyperf** (`benchmarks/pyperf_suite.py`) — process-isolated, statistically
  rigorous construction benchmark, closer to what you'd cite in a real
  comparison.

Memory footprint (`benchmarks/memory_profile.py`, `tracemalloc`-based) and
cold-import overhead (`benchmarks/import_time.py`, subprocess-based) are
measured separately as standalone scripts, since both need process-level
isolation that doesn't fit pytest-benchmark's per-call timing model.

## Reproducing these numbers

```bash
pytest benchmarks/ --benchmark-only      # construction/access/repr/eq/hash/decoration/builder
python benchmarks/pyperf_suite.py        # process-isolated construction comparison
python benchmarks/memory_profile.py      # per-instance memory footprint
python benchmarks/import_time.py         # cold-import overhead
```

## Results

Measured on Apple M5 (macOS 26.3.1), CPython 3.12.13, single run. **These
are indicative, single-machine numbers, not hardware-normalized or
CI-verified** — treat relative ordering as meaningful, absolute nanosecond
values as illustrative only. Re-run locally for numbers that matter to your
decision.

### pytest-benchmark (mean, nanoseconds unless noted)

| Operation | handwritten | InitO | dataclass | attrs |
|---|---:|---:|---:|---:|
| construction | 66 | 71 | 71 | 62 |
| attribute access | 13.6 | 13.6 | 13.6 | 13.5 |
| `__repr__` | 104 | 107 | 197 | 204 |
| `__eq__` | 62 | 67 | 67 | 49 |
| `__hash__` | 58 | 62 | 61 | 62 |
| decoration (µs) | ~2 | ~100 | ~78 | ~92 |

**InitO is at parity with handwritten/dataclasses across every runtime
operation** — and slightly ahead on equality and single-field hashing. `__eq__`
emits a field-by-field `and`-chain (`self.a == other.a and ...`), the same thing
you'd write by hand: it allocates nothing and short-circuits on the first
differing field, so it is faster than the two-tuple comparison dataclasses
generate (the `__eq__`/`__hash__` figures above predate this — re-run the
benchmark to regenerate). A single-field class hashes the field directly rather
than wrapping it in a one-element tuple. For an ordinary (non-frozen) class,
generated constructors
assign fields via plain `self.x = x` — the fastest option, and the one that
keeps CPython's key-sharing instance dict (PEP 412) intact so attribute
reads and `__eq__`/`__hash__`/`__repr__` stay at handwritten speed. When a
class is immutable — `@Value`, `@Data(frozen=True)`, or stacked on top of
`@dataclass(frozen=True)` (innermost) — the constructor assigns via a
once-bound `object.__setattr__` to bypass the blocking `__setattr__`. That
costs more to construct (~130ns, roughly 2x — a cold, once-per-object path)
but **still keeps reads fast**, because `object.__setattr__` also preserves
the key-sharing dict. `__repr__` is the fastest of the three codegen flavors
(single unrolled f-string). (An earlier 0.0.11 experiment wrote fields via
`self.__dict__["x"] = x`; it was slightly faster to construct but broke
key-sharing, silently regressing every attribute read — reverted here.)

`@Builder` fluent chain vs. a direct constructor call (both on the same
`@Data`-equipped class): the direct call took ~80ns; the four-method fluent
chain (`.builder().x().y().label().build()`) took ~250ns — expected, since
it does five method calls and allocates a Builder instance instead of one.

### pyperf construction (mean ± stddev)

Representative single-machine run: handwritten and dataclass land in the
same ~70-75ns band as InitO; attrs is a few ns faster. Run
`python benchmarks/pyperf_suite.py` locally for numbers with pyperf's full
statistical rigor (the quick sanity-check run used here used `--fast`,
which pyperf itself flags as insufficient for a stable result).

### Memory footprint (bytes/instance, 100k instances)

| Flavor | Bytes/instance |
|---|---:|
| handwritten | 96.0 |
| InitO | 96.0 |
| dataclass | 96.0 |
| attrs (slotted) | 80.0 |

InitO matches handwritten/dataclass exactly — all three use ordinary
`__dict__`-based instances. attrs is smaller here because `attrs.define`
opts into `__slots__` by default; InitO doesn't generate slotted classes
today (tracked as a possible future enhancement, not required by the
current spec).

### Cold-import overhead (mean ± stddev, 15 runs)

| Import | Time |
|---|---:|
| baseline (no import) | 0.00 ms |
| `dataclasses` (stdlib) | 4.46 ms |
| `attrs` | 9.31 ms |
| `inito` | 8.74 ms |

## Takeaways

- **Construction, attribute access, `__eq__`, `__hash__`:** InitO is at or
  within a few percent of handwritten/dataclasses — those generators emit
  exactly what you'd write by hand, and non-frozen construction uses a plain
  `self.x = x`, so the "generated code performs like handwritten code" goal
  holds up in measurement, not just in design intent. `__eq__` (an
  allocation-free `and`-chain) and single-field `__hash__` (a direct
  `hash(self.field)`) are actually a shade faster than the tuple-based forms
  dataclasses emit — measured ~20% / ~30% on the comparison itself.
- **Immutable classes** (`@Value`/`@Data(frozen=True)`/frozen-innermost) pay
  ~2x on construction only (the `object.__setattr__` bypass, a cold
  once-per-object path); their attribute reads and eq/hash/repr stay at
  handwritten speed.
- **`__repr__`:** InitO's single unrolled f-string is the fastest generated
  repr among the three codegen-based flavors, and close to handwritten.
- **Decoration time:** meaningfully higher than dataclasses (both are
  one-time, at-import costs, not per-instance) — reasonable given InitO's
  extra indirection (registry lookup, `exec()`-based method generation vs.
  dataclasses' more specialized C-accelerated path), and irrelevant to
  steady-state performance since it happens once per class, not per object.
- **Memory:** identical to handwritten/dataclasses; attrs' default slotted
  classes have a real, expected edge here.

## Dependency injection (`@Service`/`@Singleton`/`@Inject`)

`benchmarks/test_di_benchmark.py` compares the DI container against
hand-written equivalents at four points. Measured on the same machine as
above, after 0.0.10-beta added double-checked per-class locking around
singleton construction (see the [Dependency injection guide](dependency-injection.md#performance-and-safety)):

| Operation | InitO (DI) | hand-written | Verdict |
|---|---:|---:|---|
| attribute access on a resolved instance | 12 ns | 12 ns | **at parity** — zero DI-related overhead once an object is built |
| `container.get()`, warm/singleton-cached | 45 ns | 22 ns | small — a single dict lookup (fast-pathed ahead of registration/scope/cycle checks); **no lock is touched once a singleton is cached** |
| cold full-graph resolution (3-level) | ~700 ns | ~150 ns | real, one-time-per-resolution cost — quantified, not hidden |
| `@Inject`-wrapped function call | 202 ns | 25 ns | real, **every call** — but ~4x cheaper than before (see below) |

Unlike every other decorator in this library, `@Inject` and cold
`container.get()` calls are **not** claimed to be zero-overhead — only
post-construction attribute/method access on an already-resolved object
is. `@Inject` wraps a function (typically a composition-root entry point),
and resolving its container-registered parameters happens on every call.
It still inspects the wrapped function's signature and type hints **exactly
once, at decoration time**; the per-call path only checks which parameters
the caller already supplied (a name/positional-index check — no
`Signature.bind_partial` per call) and resolves the rest. Precomputing the
signature is what first brought the call cost from ~830ns to ~200ns; each
unfilled, registered parameter is then resolved by a **single** container
traversal — `_resolve_optional` (override → warm singleton → registration),
bound once at decoration — rather than the former `is_registered` check
*followed by* `get`, which trims the resolution step a further ~15% (the
`202 ns` figure predates this fold — re-run the benchmark to regenerate).
See [the Dependency injection guide](dependency-injection.md) for why this
boundary is architecturally different from every other generated member.

Concurrent first-access to a singleton from multiple threads is safe
(verified with a real `threading` reproduction: 20 threads racing a cold
`get()` construct the service exactly once and all receive the same
instance). Dependencies are resolved *before* a service's construction lock
is taken, so no thread ever holds two locks at once — a cyclic graph
resolved concurrently from opposite ends raises `CircularDependencyError`
cleanly rather than deadlocking. The lock only runs on the cold path; warm
`get()` is lock-free.

Cold resolution keeps to InitO's "reflect once, at decoration time" rule:
each dependency's autowire type (its `Optional[...]` wrapper stripped) is
computed once at `@Service` registration, not re-derived on every `get()`,
and each singleton's construction lock is created at registration too — so
the cold path is a plain dict read rather than guarding a lazily-built lock
table. Both keep the warm path untouched.
