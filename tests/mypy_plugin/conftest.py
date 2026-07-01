"""Shared helper: run mypy in-process (for coverage tracking) against a
source snippet with inito's plugin enabled, and return its exit status
and output for assertions.
"""

from __future__ import annotations

import textwrap

import mypy.api
import pytest


@pytest.fixture
def check_mypy(tmp_path):
    def _check(source: str) -> tuple[int, str]:
        source_file = tmp_path / "snippet.py"
        source_file.write_text(textwrap.dedent(source))
        config_file = tmp_path / "mypy.ini"
        config_file.write_text("[mypy]\nplugins = inito.typing.mypy_plugin\nstrict = True\n")
        out, _err, status = mypy.api.run(["--config-file", str(config_file), str(source_file)])
        # Older mypy (<1.20) fully qualifies builtins in reveal_type output
        # (`"builtins.str"`); newer mypy abbreviates to `"str"`. Normalize
        # here so every test's assertions are stable across mypy versions.
        out = out.replace('Revealed type is "builtins.', 'Revealed type is "')
        return status, out

    return _check
