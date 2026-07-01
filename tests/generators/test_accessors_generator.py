from inito.generators.accessors import GetterGenerator, SetterGenerator
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _metadata() -> ClassMetadata:
    fields = (FieldMetadata(name="a", type_hint=int), FieldMetadata(name="b", type_hint=str))
    return ClassMetadata(owner=object, fields=fields, qualified_name="Sample")


def test_getter_generator_produces_one_method_per_field():
    methods = GetterGenerator().generate_all(_metadata())
    assert [m.name for m in methods] == ["get_a", "get_b"]

    class Sample:
        def __init__(self) -> None:
            self.a = 1
            self.b = "x"

    for method in methods:
        setattr(Sample, method.name, method.callable)

    instance = Sample()
    assert instance.get_a() == 1
    assert instance.get_b() == "x"


def test_setter_generator_produces_one_method_per_field():
    methods = SetterGenerator().generate_all(_metadata())
    assert [m.name for m in methods] == ["set_a", "set_b"]

    class Sample:
        pass

    for method in methods:
        setattr(Sample, method.name, method.callable)

    instance = Sample()
    instance.set_a(1)
    instance.set_b("x")
    assert instance.a == 1
    assert instance.b == "x"


def test_no_fields_produces_no_methods():
    empty_metadata = ClassMetadata(owner=object, fields=(), qualified_name="Empty")
    assert GetterGenerator().generate_all(empty_metadata) == ()
    assert SetterGenerator().generate_all(empty_metadata) == ()
