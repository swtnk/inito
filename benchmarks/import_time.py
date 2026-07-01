"""Cold-import overhead: how much does `import inito` add to startup?

Measured via fresh subprocesses (import caching would make in-process
measurement meaningless after the first import). Run directly:

    python benchmarks/import_time.py
"""

from __future__ import annotations

import statistics
import subprocess
import sys

RUNS = 15


def _measure(import_statement: str) -> list[float]:
    code = (
        "import time; _start = time.perf_counter(); "
        f"{import_statement}; print(time.perf_counter() - _start)"
    )
    samples = []
    for _ in range(RUNS):
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=True,
        )
        samples.append(float(result.stdout.strip()))
    return samples


def main() -> None:
    """Print cold-import time for a bare interpreter, inito, dataclasses, and attrs."""
    for label, statement in (
        ("baseline (no import)", "pass"),
        ("dataclasses", "import dataclasses"),
        ("attrs", "import attrs"),
        ("inito", "import inito"),
    ):
        samples = _measure(statement)
        mean_ms = statistics.mean(samples) * 1000
        stdev_ms = statistics.stdev(samples) * 1000
        print(f"{label:>22}: {mean_ms:6.2f} ms +- {stdev_ms:4.2f} ms")


if __name__ == "__main__":
    main()
