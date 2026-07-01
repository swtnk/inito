import dataclasses

import pytest

from inito.metadata.field import MISSING, FieldMetadata


def test_field_without_default_is_required():
    field = FieldMetadata(name="x", type_hint=int)
    assert field.default is MISSING
    assert field.has_default is False
    assert field.is_required is True


def test_field_with_default_value_is_optional():
    field = FieldMetadata(name="x", type_hint=int, default=5)
    assert field.has_default is True
    assert field.is_required is False


def test_field_with_default_factory_is_optional():
    field = FieldMetadata(name="items", type_hint=list, default_factory=list)
    assert field.has_default is False
    assert field.default_factory is list
    assert field.is_required is False


def test_field_metadata_is_frozen():
    field = FieldMetadata(name="x", type_hint=int)
    with pytest.raises(dataclasses.FrozenInstanceError):
        field.name = "y"
