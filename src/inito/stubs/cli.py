"""``inito-stubgen``: emit ``.pyi`` stubs so pyright sees inito's generated members.

Run over your source, then re-run when your decorated classes change (or wire it
into pre-commit). mypy users don't need this - the bundled mypy plugin already
sees every generated member.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from inito.stubs.generator import StubgenUnavailableError, generate_stub_for_file


def _iter_py_files(paths: Iterable[str]) -> Iterator[Path]:
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            yield from sorted(p for p in path.rglob("*.py") if not p.name.startswith("."))
        elif path.suffix == ".py":
            yield path


def main(argv: list[str] | None = None) -> int:
    """Generate a sibling .pyi for every module containing inito-decorated classes."""
    parser = argparse.ArgumentParser(
        prog="inito-stubgen",
        description="Generate .pyi stubs exposing inito's generated members to pyright.",
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to scan.")
    args = parser.parse_args(argv)

    written = 0
    try:
        for py_file in _iter_py_files(args.paths):
            stub = generate_stub_for_file(py_file)
            if stub is None:
                continue
            target = py_file.with_suffix(".pyi")
            target.write_text(stub + "\n")
            print(f"wrote {target}")
            written += 1
    except StubgenUnavailableError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"generated {written} stub(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover -- module-as-script entry point
    raise SystemExit(main())
