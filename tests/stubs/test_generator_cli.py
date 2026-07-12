import shutil

import pytest

from inito.stubs import generator
from inito.stubs.cli import _iter_py_files, main
from inito.stubs.generator import StubgenUnavailableError, generate_stub_for_file

_MODEL_SRC = """
from inito import Builder, Data


@Data
class User:
    name: str
    age: int = 0


@Builder
class Request:
    path: str
"""

_needs_stubgen = pytest.mark.skipif(
    shutil.which("stubgen") is None, reason="stubgen (mypy) not installed"
)


def test_iter_py_files_walks_directories_and_filters(tmp_path):
    (tmp_path / "a.py").write_text("x = 1")
    (tmp_path / "b.txt").write_text("not python")
    (tmp_path / ".hidden.py").write_text("h = 1")
    lone = tmp_path / "lone.py"
    lone.write_text("y = 2")

    from_dir = list(_iter_py_files([str(tmp_path)]))
    from_file = list(_iter_py_files([str(lone)]))
    from_non_py = list(_iter_py_files([str(tmp_path / "b.txt")]))

    assert (tmp_path / "a.py") in from_dir  # directories are walked
    assert all(path.suffix == ".py" for path in from_dir)  # .txt filtered out
    assert (tmp_path / ".hidden.py") not in from_dir  # dotfiles skipped
    assert from_file == [lone]  # a direct .py path is yielded as-is
    assert from_non_py == []  # a direct non-.py, non-dir path yields nothing


@_needs_stubgen
def test_generate_stub_for_file_augments_with_generated_members(tmp_path):
    module = tmp_path / "models.py"
    module.write_text(_MODEL_SRC)

    stub = generate_stub_for_file(module)
    assert stub is not None
    assert "def get_name(self) -> str:" in stub
    assert "class Builder:" in stub


@_needs_stubgen
def test_cli_writes_a_sibling_pyi(tmp_path, capsys):
    module = tmp_path / "models.py"
    module.write_text(_MODEL_SRC)

    assert main([str(module)]) == 0
    assert (tmp_path / "models.pyi").exists()
    assert "generated 1 stub(s)" in capsys.readouterr().out


def test_file_without_inito_classes_is_skipped(tmp_path):
    module = tmp_path / "plain.py"
    module.write_text("x = 1\n")
    assert generate_stub_for_file(module) is None


def test_unimportable_module_is_skipped(tmp_path):
    module = tmp_path / "broken.py"
    module.write_text("import a_module_that_does_not_exist\n")
    assert generate_stub_for_file(module) is None


def test_missing_stubgen_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(generator.shutil, "which", lambda _name: None)
    with pytest.raises(StubgenUnavailableError):
        generator._stubgen_source(tmp_path / "anything.py")


def test_cli_scans_directories(tmp_path):
    (tmp_path / "plain.py").write_text("x = 1\n")
    assert main([str(tmp_path)]) == 0  # no inito classes -> generates nothing, exits clean


def test_cli_reports_missing_stubgen(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(generator.shutil, "which", lambda _name: None)
    module = tmp_path / "models.py"
    module.write_text(_MODEL_SRC)

    assert main([str(module)]) == 2
    assert "install inito[stubgen]" in capsys.readouterr().err
