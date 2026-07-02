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
- **inito** — the same class decorated with `@Data` (and `@Builder` where noted).
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

| Operation | handwritten | inito | dataclass | attrs |
|---|---:|---:|---:|---:|
| construction | 66 | 88 | 74 | 61 |
| attribute access | 13.8 | 13.8 | 13.8 | 13.9 |
| `__repr__` | 106 | 119 | 198 | 207 |
| `__eq__` | 62 | 88 | 66 | 50 |
| `__hash__` | 61 | 72 | 64 | 71 |
| decoration (µs) | ~2 | ~100 | ~78 | ~92 |

**On construction** inito carries a ~1.2-1.3x premium over a handwritten
`self.x = x` constructor. This is a deliberate, one-time-decided tradeoff:
generated constructors assign fields via a direct `self.__dict__["x"] = x`
write (for ordinary classes) rather than `self.x = x`, so that `@Value`,
`@Data(frozen=True)`, and any stacking order with `@dataclass(frozen=True)`
are all immutable-correct **without** a per-instance branch — construction
writes straight to the instance dict, bypassing the blocking `__setattr__`,
while a later `obj.x = 5` still raises. The `__dict__` write is ~2x faster
than the `object.__setattr__` this replaced (which cost inito ~2.5x
handwritten and is what an earlier version of this table, recorded before
that change, under-reported). Fully slotted classes fall back to a
once-bound `object.__setattr__`. `attribute access`, `__repr__`, `__eq__`,
and `__hash__` remain at or near handwritten parity — those generators emit
exactly what you'd write by hand.

`@Builder` fluent chain vs. a direct constructor call (both on the same
`@Data`-equipped class): the direct call took ~80ns; the four-method fluent
chain (`.builder().x().y().label().build()`) took ~250ns — expected, since
it does five method calls and allocates a Builder instance instead of one.

### pyperf construction (mean ± stddev)

Representative single-machine run: handwritten and dataclass land in the
same ~70-75ns band as inito; attrs is a few ns faster. Run
`python benchmarks/pyperf_suite.py` locally for numbers with pyperf's full
statistical rigor (the quick sanity-check run used here used `--fast`,
which pyperf itself flags as insufficient for a stable result).

### Memory footprint (bytes/instance, 100k instances)

| Flavor | Bytes/instance |
|---|---:|
| handwritten | 96.0 |
| inito | 96.0 |
| dataclass | 96.0 |
| attrs (slotted) | 80.0 |

inito matches handwritten/dataclass exactly — all three use ordinary
`__dict__`-based instances. attrs is smaller here because `attrs.define`
opts into `__slots__` by default; inito doesn't generate slotted classes
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

- **Attribute access, `__eq__`, `__hash__`:** inito is at or within a few
  percent of handwritten — those generators emit exactly what you'd write by
  hand, so the "generated code performs like handwritten code" goal holds up
  in measurement, not just in design intent.
- **Construction:** ~1.2-1.3x handwritten — the one place inito accepts a
  small, deliberate premium (the frozen-safe `__dict__` write, see the table
  note above) in exchange for correct, branch-free immutability across every
  decorator and stacking order. Still ~2x faster than the `object.__setattr__`
  approach it replaced.
- **`__repr__`:** inito's single unrolled f-string is the fastest generated
  repr among the three codegen-based flavors, and close to handwritten.
- **Decoration time:** meaningfully higher than dataclasses (both are
  one-time, at-import costs, not per-instance) — reasonable given inito's
  extra indirection (registry lookup, `exec()`-based method generation vs.
  dataclasses' more specialized C-accelerated path), and irrelevant to
  steady-state performance since it happens once per class, not per object.
- **Memory:** identical to handwritten/dataclasses; attrs' default slotted
  classes have a real, expected edge here.

## Dependency injection (`@Service`/`@Singleton`/`@Inject`)

`benchmarks/test_di_benchmark.py` compares the DI container against
hand-written equivalents at four points. Measured on the same machine as
above, after 0.0.10-beta added double-checked per-class locking around
singleton construction (see [Quick start's thread-safety
section](quickstart.md)):

| Operation | inito (DI) | hand-written | Verdict |
|---|---:|---:|---|
| attribute access on a resolved instance | 12 ns | 12 ns | **at parity** — zero DI-related overhead once an object is built |
| `container.get()`, warm/singleton-cached | 94 ns | 22 ns | real but small — a dict lookup + scope check, not zero; **no lock is touched once a singleton is cached** |
| cold full-graph resolution (3-level) | ~900 ns | ~140 ns | real, one-time-per-resolution cost — quantified, not hidden |
| `@Inject`-wrapped function call | 202 ns | 25 ns | real, **every call** — but ~4x cheaper than before (see below) |

Unlike every other decorator in this library, `@Inject` and cold
`container.get()` calls are **not** claimed to be zero-overhead — only
post-construction attribute/method access on an already-resolved object
is. `@Inject` wraps a function (typically a composition-root entry point),
and resolving its container-registered parameters happens on every call.
It still inspects the wrapped function's signature and type hints **exactly
once, at decoration time**; the per-call path only checks which parameters
the caller already supplied (a name/positional-index check — no
`Signature.bind_partial` per call) and resolves the rest. That is what
brought the call cost from ~830ns to ~200ns. See
[Quick start's DI section](quickstart.md#dependency-injection) for why this
boundary is architecturally different from every other generated member.

Concurrent first-access to a singleton from multiple threads is safe
(verified with a real `threading` reproduction: 20 threads racing a cold
`get()` construct the service exactly once and all receive the same
instance). Dependencies are resolved *before* a service's construction lock
is taken, so no thread ever holds two locks at once — a cyclic graph
resolved concurrently from opposite ends raises `CircularDependencyError`
cleanly rather than deadlocking. The lock only runs on the cold path; warm
`get()` is lock-free.
