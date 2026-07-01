from inito.generators.base import generate_method
from inito.generators.constructor import RequiredArgsConstructorGenerator
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _metadata(fields: tuple) -> ClassMetadata:
    return ClassMetadata(owner=object, fields=fields, qualified_name="Sample")


def test_only_required_fields_are_accepted_as_parameters():
    fields = (
        FieldMetadata(name="a", type_hint=int),
        FieldMetadata(name="b", type_hint=int, default=2),
    )
    generated = generate_method(RequiredArgsConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    instance = Sample(1)
    assert instance.a == 1
    assert instance.b == 2


def test_optional_field_cannot_be_overridden_via_constructor():
    fields = (FieldMetadata(name="a", type_hint=int, default=5),)
    generated = generate_method(RequiredArgsConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    instance = Sample()
    assert instance.a == 5


def test_default_factory_is_called_fresh_per_instance():
    fields = (
        FieldMetadata(name="required", type_hint=int),
        FieldMetadata(name="items", type_hint=list, default_factory=list),
    )
    generated = generate_method(RequiredArgsConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    first = Sample(1)
    second = Sample(2)
    first.items.append(1)
    assert second.items == []
    assert first.items is not second.items


def test_all_fields_optional_produces_no_argument_constructor():
    fields = (FieldMetadata(name="a", type_hint=int, default=1),)
    generated = generate_method(RequiredArgsConstructorGenerator(), _metadata(fields))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    assert Sample().a == 1


def test_no_fields_produces_no_op_constructor():
    generated = generate_method(RequiredArgsConstructorGenerator(), _metadata(()))

    class Sample:
        pass

    Sample.__init__ = generated.callable
    Sample()
