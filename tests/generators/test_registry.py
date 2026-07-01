import pytest

from inito.exceptions.errors import DuplicateGeneratorError
from inito.generators.registry import GeneratorRegistry


def test_register_and_get_roundtrip():
    registry = GeneratorRegistry()
    sentinel = object()
    registry.register("capability", sentinel)
    assert registry.get("capability") is sentinel


def test_register_duplicate_capability_raises():
    registry = GeneratorRegistry()
    registry.register("capability", object())
    with pytest.raises(DuplicateGeneratorError):
        registry.register("capability", object())


def test_get_missing_capability_raises_key_error():
    registry = GeneratorRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")
