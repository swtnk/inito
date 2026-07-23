import dataclasses

import pytest

from inito.exceptions.errors import InvalidFieldDefinitionError
from inito.metadata.field import MISSING, FieldMetadata, FieldSpec, field


def test_field_builds_a_default_factory_spec():
    spec = field(default_factory=list)
    assert isinstance(spec, FieldSpec)
    assert spec.default is MISSING
    assert spec.default_factory is list


def test_field_builds_a_plain_default_spec():
    spec = field(default=5)
    assert spec.default == 5
    assert spec.default_factory is None


def test_field_rejects_both_default_and_default_factory():
    with pytest.raises(InvalidFieldDefinitionError, match="both default and default_factory"):
        field(default=1, default_factory=list)


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
