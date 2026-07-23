import pytest

from inito.exceptions.errors import InvalidFieldDefinitionError
from inito.generators.base import generate_method
from inito.generators.constructor import ConstructorGenerator
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _metadata(fields: tuple) -> ClassMetadata:
    return ClassMetadata(owner=object, fields=fields, qualified_name="Sample")


def test_signature_preserves_declaration_order():
    fields = (
        FieldMetadata(name="a", type_hint=int),
        FieldMetadata(name="b", type_hint=int, default=2),
    )
    generated = generate_method(ConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    instance = Sample(1)
    assert instance.a == 1
    assert instance.b == 2


def test_required_field_after_optional_is_rejected():
    fields = (
        FieldMetadata(name="b", type_hint=int, default=2),
        FieldMetadata(name="a", type_hint=int),
    )
    with pytest.raises(InvalidFieldDefinitionError, match="required field 'a'"):
        generate_method(ConstructorGenerator(), _metadata(fields))


def test_default_value_can_be_overridden():
    fields = (FieldMetadata(name="x", type_hint=int, default=5),)
    generated = generate_method(ConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    assert Sample(x=9).x == 9
    assert Sample().x == 5


def test_default_factory_is_called_fresh_per_instance():
    fields = (FieldMetadata(name="items", type_hint=list, default_factory=list),)
    generated = generate_method(ConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    first = Sample()
    second = Sample()
    first.items.append(1)
    assert second.items == []
    assert first.items is not second.items


def test_no_fields_produces_no_op_constructor():
    generated = generate_method(ConstructorGenerator(), _metadata(()))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    Sample()
