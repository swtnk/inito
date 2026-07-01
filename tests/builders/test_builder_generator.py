import pytest

from inito.builders.builder_generator import BuilderGenerator, BuilderOptions
from inito.exceptions.errors import BuilderValidationError
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _metadata(owner: type, fields: tuple) -> ClassMetadata:
    return ClassMetadata(owner=owner, fields=fields, qualified_name=owner.__name__)


def test_builder_class_supports_fluent_chaining_and_build():
    class Point:
        pass

    fields = (FieldMetadata(name="x", type_hint=int), FieldMetadata(name="y", type_hint=int))
    builder_class = BuilderGenerator().build_builder_class(
        _metadata(Point, fields), BuilderOptions()
    )

    instance = builder_class().x(1).y(2).build()
    assert isinstance(instance, Point)
    assert instance.x == 1
    assert instance.y == 2


def test_builder_uses_default_value_when_field_not_set():
    class Point:
        pass

    fields = (FieldMetadata(name="x", type_hint=int, default=9),)
    builder_class = BuilderGenerator().build_builder_class(
        _metadata(Point, fields), BuilderOptions()
    )

    assert builder_class().build().x == 9


def test_builder_uses_default_factory_fresh_per_builder():
    class Sample:
        pass

    fields = (FieldMetadata(name="items", type_hint=list, default_factory=list),)
    builder_class = BuilderGenerator().build_builder_class(
        _metadata(Sample, fields), BuilderOptions()
    )

    first = builder_class().build()
    second = builder_class().build()
    first.items.append(1)
    assert second.items == []


def test_build_raises_when_required_field_not_set():
    class Sample:
        pass

    fields = (FieldMetadata(name="x", type_hint=int),)
    builder_class = BuilderGenerator().build_builder_class(
        _metadata(Sample, fields), BuilderOptions()
    )

    with pytest.raises(BuilderValidationError):
        builder_class().build()


def test_setter_prefix_option_renames_fluent_methods():
    class Sample:
        pass

    fields = (FieldMetadata(name="x", type_hint=int),)
    options = BuilderOptions(setter_prefix="with_")
    builder_class = BuilderGenerator().build_builder_class(_metadata(Sample, fields), options)

    instance = builder_class().with_x(5).build()
    assert instance.x == 5
    assert not hasattr(builder_class(), "x")


def test_build_method_name_option_renames_build_method():
    class Sample:
        pass

    fields = (FieldMetadata(name="x", type_hint=int, default=1),)
    options = BuilderOptions(build_method_name="create")
    builder_class = BuilderGenerator().build_builder_class(_metadata(Sample, fields), options)

    instance = builder_class().create()
    assert instance.x == 1
    assert not hasattr(builder_class(), "build")


def test_build_factory_returns_a_new_builder_instance():
    class Sample:
        pass

    metadata = _metadata(Sample, (FieldMetadata(name="x", type_hint=int, default=1),))
    generator = BuilderGenerator()
    Sample.Builder = generator.build_builder_class(metadata, BuilderOptions())

    builder_instance = generator.build_factory(metadata)(Sample)
    assert isinstance(builder_instance, Sample.Builder)


def test_to_builder_prepopulates_builder_from_instance():
    class Point:
        pass

    fields = (FieldMetadata(name="x", type_hint=int), FieldMetadata(name="y", type_hint=int))
    metadata = _metadata(Point, fields)
    generator = BuilderGenerator()
    Point.Builder = generator.build_builder_class(metadata, BuilderOptions())

    original = Point()
    original.x, original.y = 1, 2

    rebuilt = generator.build_to_builder(metadata)(original).y(5).build()
    assert rebuilt.x == 1
    assert rebuilt.y == 5


def test_no_fields_produces_working_builder():
    class Empty:
        pass

    builder_class = BuilderGenerator().build_builder_class(_metadata(Empty, ()), BuilderOptions())
    instance = builder_class().build()
    assert isinstance(instance, Empty)


def test_builder_options_defaults():
    options = BuilderOptions()
    assert options.to_builder is False
    assert options.setter_prefix == ""
    assert options.build_method_name == "build"
