import dataclasses
import typing

import pytest

from inito.exceptions.errors import AnnotationResolutionError, InvalidFieldDefinitionError
from inito.metadata.class_metadata import METADATA_ATTRIBUTE
from inito.metadata.extractor import MetadataExtractor
from inito.metadata.field import MISSING, field


def test_rejects_a_mutable_literal_default():
    class Sample:
        items: list = []  # noqa: RUF012 -- the footgun this test asserts is rejected

    with pytest.raises(InvalidFieldDefinitionError, match="mutable default"):
        MetadataExtractor().extract(Sample)


def test_field_default_factory_is_read_and_sentinel_removed_from_class():
    class Sample:
        items: list = field(default_factory=list)

    metadata = MetadataExtractor().extract(Sample)
    assert metadata.fields[0].default is MISSING
    assert metadata.fields[0].default_factory is list
    assert "items" not in Sample.__dict__


def test_field_plain_default_is_read_and_left_on_class():
    class Sample:
        n: int = field(default=5)

    metadata = MetadataExtractor().extract(Sample)
    assert metadata.fields[0].default == 5
    assert Sample.n == 5


def test_field_rejects_a_mutable_plain_default():
    class Sample:
        items: list = field(default=[])

    with pytest.raises(InvalidFieldDefinitionError, match="mutable default"):
        MetadataExtractor().extract(Sample)


def test_rejects_a_non_identifier_field_name():
    sample = type("Sample", (), {"__annotations__": {"bad-name": int}})
    with pytest.raises(InvalidFieldDefinitionError, match="not a valid Python identifier"):
        MetadataExtractor().extract(sample)


def test_rejects_a_keyword_field_name():
    sample = type("Sample", (), {"__annotations__": {"class": int}})
    with pytest.raises(InvalidFieldDefinitionError, match="not a valid Python identifier"):
        MetadataExtractor().extract(sample)


def test_rejects_a_reserved_prefix_field_name():
    class Sample:
        _inito_x: int = 1

    with pytest.raises(InvalidFieldDefinitionError, match="reserved"):
        MetadataExtractor().extract(Sample)


def test_inherited_field_spec_is_read_without_touching_the_base():
    class Base:
        items: list = field(default_factory=list)

    class Sub(Base):
        n: int = 1

    metadata = MetadataExtractor().extract(Sub)
    by_name = {f.name: f for f in metadata.fields}
    assert by_name["items"].default_factory is list
    # The inherited sentinel must stay on Base, never be deleted off Sub.
    assert "items" in Base.__dict__
    assert "items" not in Sub.__dict__


def test_extracts_plain_annotated_fields_in_order():
    class Sample:
        a: int
        b: str = "x"

    metadata = MetadataExtractor().extract(Sample)
    assert metadata.field_names() == ("a", "b")
    assert metadata.fields[0].default is MISSING
    assert metadata.fields[1].default == "x"


def test_caches_metadata_on_class_and_reuses_it():
    class Sample:
        a: int

    extractor = MetadataExtractor()
    first = extractor.extract(Sample)
    second = extractor.extract(Sample)
    assert first is second
    assert Sample.__dict__[METADATA_ATTRIBUTE] is first


def test_subclass_does_not_inherit_parent_cached_metadata():
    class Base:
        a: int

    class Sub(Base):
        b: int

    extractor = MetadataExtractor()
    base_metadata = extractor.extract(Base)
    sub_metadata = extractor.extract(Sub)
    assert base_metadata is not sub_metadata
    assert sub_metadata.field_names() == ("a", "b")


def test_inherited_fields_come_before_subclass_fields():
    class Base:
        a: int = 1

    class Sub(Base):
        b: int

    metadata = MetadataExtractor().extract(Sub)
    assert metadata.field_names() == ("a", "b")


def test_class_var_fields_are_excluded():
    class Sample:
        counter: typing.ClassVar[int] = 0
        a: int

    metadata = MetadataExtractor().extract(Sample)
    assert metadata.field_names() == ("a",)


def test_dataclass_fields_use_dataclass_defaults_and_factories():
    @dataclasses.dataclass
    class Sample:
        a: int
        b: list = dataclasses.field(default_factory=list)

    metadata = MetadataExtractor().extract(Sample)
    a_field, b_field = metadata.fields
    assert a_field.default is MISSING
    assert b_field.default_factory is list


def test_unresolvable_annotation_raises_annotation_resolution_error():
    class Sample:
        a: "DoesNotExist"  # noqa: F821 -- intentionally unresolvable

    with pytest.raises(AnnotationResolutionError):
        MetadataExtractor().extract(Sample)


class _FakeFieldInfo:
    # Duck-typed stand-in for pydantic's FieldInfo, so these tests read a
    # model's field model without depending on pydantic being installed.
    def __init__(self, annotation, *, default=MISSING, default_factory=None, required=False):
        self.annotation = annotation
        self.default = default
        self.default_factory = default_factory
        self._required = required

    def is_required(self) -> bool:
        return self._required


def _fake_pydantic_model(**model_fields):
    return type(
        "FakeModel",
        (),
        {"model_fields": dict(model_fields), "__pydantic_validator__": object()},
    )


def test_pydantic_fields_read_required_default_and_factory_from_model_fields():
    model = _fake_pydantic_model(
        name=_FakeFieldInfo(str, required=True),
        age=_FakeFieldInfo(int, default=0),
        tags=_FakeFieldInfo(list, default_factory=list),
    )
    fields = {field.name: field for field in MetadataExtractor().extract(model).fields}

    assert fields["name"].type_hint is str
    assert fields["name"].is_required  # required -> no default
    assert fields["age"].default == 0  # literal default read from FieldInfo
    assert not fields["age"].is_required
    assert fields["tags"].default_factory is list  # factory read from FieldInfo
    assert not fields["tags"].is_required
