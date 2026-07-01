from inito.generators.base import GeneratedMethod, generate_method, generate_methods
from inito.metadata.class_metadata import ClassMetadata


class _EchoGenerator:
    method_name = "echo"

    def generate_source(self, metadata: ClassMetadata) -> str:
        return "def echo(self):\n    return 'echo'\n"

    def build_globals(self, metadata: ClassMetadata) -> dict:
        return {}


class _MultiGenerator:
    def generate_all(self, metadata: ClassMetadata) -> tuple:
        return (GeneratedMethod(name="a", callable=lambda self: "a"),)


def _metadata() -> ClassMetadata:
    return ClassMetadata(owner=object, fields=(), qualified_name="Sample")


def test_generate_method_builds_generated_method():
    generated = generate_method(_EchoGenerator(), _metadata())
    assert generated.name == "echo"
    assert generated.callable(None) == "echo"


def test_generate_methods_delegates_to_generate_all():
    generated = generate_methods(_MultiGenerator(), _metadata())
    assert [g.name for g in generated] == ["a"]
