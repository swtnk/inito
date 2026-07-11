"""Generate ``.pyi`` stubs for inito modules: mypy stubgen base + inito augmentation.

stubgen (from mypy, invoked as a subprocess) produces a complete, correct base
stub from the source; the module is then imported so ``augment`` can inject the
runtime-generated members. inito's own runtime stays zero-dependency - this tool
is opt-in (``pip install inito[stubgen]``).
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from types import ModuleType

from inito.metadata.class_metadata import METADATA_ATTRIBUTE
from inito.stubs.augment import augment_stub


class StubgenUnavailableError(RuntimeError):
    """Raised when mypy's stubgen executable is not on PATH."""


def generate_stub_for_file(path: Path) -> str | None:
    """Return the augmented .pyi source for path, or None if it has no inito classes."""
    module = _import_module(path)
    if module is None or not _has_inito_class(module):
        return None
    return augment_stub(_stubgen_source(path), module)


def _has_inito_class(module: ModuleType) -> bool:
    return any(
        isinstance(obj, type) and METADATA_ATTRIBUTE in obj.__dict__
        for obj in vars(module).values()
    )


def _import_module(path: Path) -> ModuleType | None:
    name = f"_inito_stub_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # an un-importable module (missing deps, side effects) is skipped
        return None
    finally:
        sys.modules.pop(name, None)
    module.__name__ = path.stem  # so augment resolves in-module names naturally
    return module


def _stubgen_source(path: Path) -> str:
    if shutil.which("stubgen") is None:
        raise StubgenUnavailableError(
            "stubgen (from mypy) is required; install it with: pip install inito[stubgen]"
        )
    with tempfile.TemporaryDirectory() as out_dir:
        subprocess.run(
            ["stubgen", "-o", out_dir, str(path)],
            check=True,
            capture_output=True,
        )
        # stubgen mirrors the input path under out_dir; there's exactly one .pyi.
        generated = next(Path(out_dir).rglob(f"{path.stem}.pyi"))
        return generated.read_text()
