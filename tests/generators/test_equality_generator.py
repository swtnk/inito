from inito.generators.base import generate_method
from inito.generators.equality import EqGenerator, HashGenerator
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _make_class(name: str, fields: tuple, bases: tuple = ()) -> type:
    cls = type(name, bases, {})
    metadata = ClassMetadata(owner=cls, fields=fields, qualified_name=name)
    cls.__init__ = lambda self, **kwargs: self.__dict__.update(kwargs)
    cls.__eq__ = generate_method(EqGenerator(), metadata).callable
    cls.__hash__ = generate_method(HashGenerator(), metadata).callable
    return cls


def test_equal_instances_compare_equal_and_hash_equal():
    fields = (FieldMetadata(name="a", type_hint=int), FieldMetadata(name="b", type_hint=int))
    sample = _make_class("Sample", fields)
    assert sample(a=1, b=2) == sample(a=1, b=2)
    assert hash(sample(a=1, b=2)) == hash(sample(a=1, b=2))


def test_unequal_instances_compare_unequal():
    fields = (FieldMetadata(name="a", type_hint=int),)
    sample = _make_class("Sample", fields)
    assert sample(a=1) != sample(a=2)


def test_different_class_returns_not_implemented():
    fields = (FieldMetadata(name="a", type_hint=int),)
    sample = _make_class("Sample", fields)
    other = _make_class("Other", fields)
    assert sample(a=1).__eq__(other(a=1)) is NotImplemented


def test_subclass_instance_is_not_equal_via_strict_class_check():
    fields = (FieldMetadata(name="a", type_hint=int),)
    sample = _make_class("Sample", fields)
    sub = _make_class("Sub", fields, bases=(sample,))
    assert sample(a=1).__eq__(sub(a=1)) is NotImplemented


def test_empty_fields_hash_and_eq():
    sample = _make_class("Sample", ())
    assert sample() == sample()
    assert hash(sample()) == hash(sample())
