"""Regression guard: every example script must pass mypy --strict with the
plugin enabled. If the plugin breaks on a real usage pattern, this fails.
"""

from __future__ import annotations

from pathlib import Path

import mypy.api

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def test_all_examples_pass_mypy_strict_with_plugin(tmp_path):
    config_file = tmp_path / "mypy.ini"
    config_file.write_text("[mypy]\nplugins = inito.typing.mypy_plugin\nstrict = True\n")

    out, _err, status = mypy.api.run(["--config-file", str(config_file), str(EXAMPLES_DIR)])

    assert status == 0, out
