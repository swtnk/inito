"""The acid test: generated stubs make pyright see every generated member.

Skipped unless both pyright and stubgen are installed; runs in the dedicated CI
`pyright` job. Proves the same code that errors under pyright without stubs
type-checks cleanly once `inito-stubgen` has run.
"""

import json
import shutil
import subprocess

import pytest

from inito.stubs.cli import main

pytestmark = pytest.mark.skipif(
    shutil.which("pyright") is None or shutil.which("stubgen") is None,
    reason="pyright and stubgen are required for the end-to-end typing test",
)

_MODELS = """
from inito import Builder, Data


@Data
class User:
    name: str
    age: int = 0


@Builder
class Request:
    path: str
    method: str = "GET"
"""

_CONSUMER = """
from models import Request, User

user = User("Ada", 30)
name: str = user.get_name()
user.set_age(31)

request = Request.builder().path("/x").method("POST").build()
path: str = request.path
"""


def _pyright_error_count(directory) -> int:
    # Run with cwd=directory so pyright resolves the local `models` import.
    result = subprocess.run(
        ["pyright", "--outputjson", "."],
        cwd=str(directory),
        capture_output=True,
        text=True,
    )
    return int(json.loads(result.stdout)["summary"]["errorCount"])


def test_generated_stubs_make_pyright_see_generated_members(tmp_path):
    (tmp_path / "models.py").write_text(_MODELS)
    (tmp_path / "consumer.py").write_text(_CONSUMER)

    assert _pyright_error_count(tmp_path) > 0  # get_name/set_age/builder unknown without stubs

    assert main([str(tmp_path / "models.py")]) == 0

    assert _pyright_error_count(tmp_path) == 0  # every generated member now visible
