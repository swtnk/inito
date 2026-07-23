"""The DI layer is imported lazily, so ``import inito`` stays DI-free."""

import subprocess
import sys

import pytest

import inito


def test_importing_inito_does_not_load_the_di_layer():
    code = "import sys, inito; print(any(m.startswith('inito.di') for m in sys.modules))"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "False"


def test_lazy_di_names_resolve_from_the_top_level():
    from inito import Container, Inject, Service, Singleton

    assert all(obj is not None for obj in (Container, Service, Singleton, Inject))


def test_lazy_di_names_resolve_via_attribute_access():
    assert inito.Factory is not None
    assert inito.default_container is not None


def test_unknown_top_level_attribute_raises():
    with pytest.raises(AttributeError, match="has no attribute 'Nonexistent'"):
        inito.Nonexistent  # noqa: B018 -- accessing it is the point of the test


def test_dir_lists_the_public_api():
    names = dir(inito)
    assert "Data" in names
    assert "Container" in names
    assert names == sorted(names)


def test_lazy_di_names_resolve_from_the_decorators_package():
    import inito.decorators as decorators

    assert decorators.Service is not None
    with pytest.raises(AttributeError, match="has no attribute 'Nope'"):
        decorators.Nope  # noqa: B018 -- accessing it is the point of the test
