import inito.core.attach as attach_module
from inito.core.attach import attach_capability, attach_method
from inito.generators.base import GeneratedMethod
from inito.generators.registry import GeneratorRegistry
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def test_attach_method_sets_attribute_and_module():
    class Sample:
        pass

    def greet(self) -> str:
        return "hi"

    attach_method(Sample, GeneratedMethod(name="greet", callable=greet))
    assert Sample().greet() == "hi"
    assert Sample.greet.__module__ == Sample.__module__


def test_attach_capability_attaches_single_method_generator(monkeypatch):
    class Sample:
        pass

    metadata = ClassMetadata(
        owner=Sample, fields=(FieldMetadata(name="a", type_hint=int),), qualified_name="Sample"
    )
    registry = GeneratorRegistry()

    class _SingleGenerator:
        method_name = "identify"

        def generate_source(self, metadata: ClassMetadata) -> str:
            return "def identify(self):\n    return 'single'\n"

        def build_globals(self, metadata: ClassMetadata) -> dict:
            return {}

    registry.register("identify", _SingleGenerator())
    monkeypatch.setattr(attach_module, "default_registry", registry)

    attach_capability(Sample, metadata, "identify")
    assert Sample().identify() == "single"


def test_attach_capability_attaches_multi_method_generator(monkeypatch):
    class Sample:
        pass

    metadata = ClassMetadata(owner=Sample, fields=(), qualified_name="Sample")
    registry = GeneratorRegistry()

    class _MultiGenerator:
        def generate_all(self, metadata: ClassMetadata) -> tuple:
            return (
                GeneratedMethod(name="a", callable=lambda self: "a"),
                GeneratedMethod(name="b", callable=lambda self: "b"),
            )

    registry.register("multi", _MultiGenerator())
    monkeypatch.setattr(attach_module, "default_registry", registry)

    attach_capability(Sample, metadata, "multi")
    assert Sample().a() == "a"
    assert Sample().b() == "b"
