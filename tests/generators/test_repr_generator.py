from inito.generators.base import generate_method
from inito.generators.repr_ import ReprGenerator
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def test_repr_lists_every_field_with_class_name():
    class Sample:
        def __init__(self, a: int, b: str) -> None:
            self.a = a
            self.b = b

    fields = (FieldMetadata(name="a", type_hint=int), FieldMetadata(name="b", type_hint=str))
    metadata = ClassMetadata(owner=Sample, fields=fields, qualified_name="Sample")
    generated = generate_method(ReprGenerator(), metadata)
    Sample.__repr__ = generated.callable

    instance = Sample(1, "x")
    assert repr(instance) == "Sample(a=1, b='x')"


def test_repr_with_no_fields():
    class Empty:
        pass

    metadata = ClassMetadata(owner=Empty, fields=(), qualified_name="Empty")
    generated = generate_method(ReprGenerator(), metadata)
    Empty.__repr__ = generated.callable
    assert repr(Empty()) == "Empty()"
