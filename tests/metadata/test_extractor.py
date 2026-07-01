import dataclasses
import typing

import pytest

from inito.exceptions.errors import AnnotationResolutionError
from inito.metadata.class_metadata import METADATA_ATTRIBUTE
from inito.metadata.extractor import MetadataExtractor
from inito.metadata.field import MISSING


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
