import pytest

from inito.exceptions.errors import InvalidFieldDefinitionError
from inito.generators.base import generate_method
from inito.generators.constructor import NoArgsConstructorGenerator
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _metadata(fields: tuple, qualified_name: str = "Sample") -> ClassMetadata:
    return ClassMetadata(owner=object, fields=fields, qualified_name=qualified_name)


def test_assigns_every_field_its_default_value():
    fields = (
        FieldMetadata(name="a", type_hint=int, default=1),
        FieldMetadata(name="b", type_hint=str, default="x"),
    )
    generated = generate_method(NoArgsConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    instance = Sample()
    assert instance.a == 1
    assert instance.b == "x"


def test_default_factory_is_called_fresh_per_instance():
    fields = (FieldMetadata(name="items", type_hint=list, default_factory=list),)
    generated = generate_method(NoArgsConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    first = Sample()
    second = Sample()
    first.items.append(1)
    assert second.items == []
    assert first.items is not second.items


def test_no_fields_produces_no_op_constructor():
    generated = generate_method(NoArgsConstructorGenerator(), _metadata(()))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    Sample()


def test_required_field_raises_invalid_field_definition_error():
    fields = (FieldMetadata(name="required", type_hint=int),)
    with pytest.raises(InvalidFieldDefinitionError):
        generate_method(NoArgsConstructorGenerator(), _metadata(fields, "Sample"))
