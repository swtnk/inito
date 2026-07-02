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


def test_repr_handles_arbitrary_dynamic_class_names():
    # Frameworks build classes dynamically via ``type(name, ...)``, and that
    # name may contain quotes/whitespace/injection payloads. The class name is
    # passed through globals rather than baked into the ``exec``'d source, so
    # such a name must render verbatim without crashing or executing anything.
    for hostile_name in (
        'Weird"Name',
        "Has Space",
        'q"; import os; os.system("echo pwned")  #',
        "Ünïcodé",
    ):
        cls = type(hostile_name, (), {})
        fields = (FieldMetadata(name="x", type_hint=int),)
        metadata = ClassMetadata(owner=cls, fields=fields, qualified_name="Dynamic")
        generated = generate_method(ReprGenerator(), metadata)
        cls.__repr__ = generated.callable

        instance = cls()
        instance.x = 1
        assert repr(instance) == f"{hostile_name}(x=1)"
