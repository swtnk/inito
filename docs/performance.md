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
| construction | 74.0 | 79.4 | 79.3 | 70.0 |
| attribute access | 22.1 | 22.0 | 22.2 | 22.4 |
| `__repr__` | 119.0 | 123.7 | 217.7 | 265.9 |
| `__eq__` | 74.3 | 79.3 | 78.4 | 61.1 |
| `__hash__` | 71.6 | 73.2 | 73.4 | 78.6 |
| decoration (µs) | 1.8 | 100.7 | 77.7 | 91.7 |

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

- **Construction, attribute access, `__eq__`, `__hash__`:** inito is within
  a few percent of handwritten/dataclasses/attrs — the "generated code
  performs like handwritten code" goal holds up in measurement, not just in
  design intent.
- **`__repr__`:** inito's single unrolled f-string is the fastest generated
  repr among the three codegen-based flavors, and close to handwritten.
- **Decoration time:** meaningfully higher than dataclasses (both are
  one-time, at-import costs, not per-instance) — reasonable given inito's
  extra indirection (registry lookup, `exec()`-based method generation vs.
  dataclasses' more specialized C-accelerated path), and irrelevant to
  steady-state performance since it happens once per class, not per object.
- **Memory:** identical to handwritten/dataclasses; attrs' default slotted
  classes have a real, expected edge here.
