from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


def _fields():
    return (
        FieldMetadata(name="required", type_hint=int),
        FieldMetadata(name="optional", type_hint=int, default=1),
    )


def test_field_names_preserves_declaration_order():
    metadata = ClassMetadata(owner=object, fields=_fields(), qualified_name="X")
    assert metadata.field_names() == ("required", "optional")


def test_required_and_optional_fields_partition_correctly():
    metadata = ClassMetadata(owner=object, fields=_fields(), qualified_name="X")
    assert [f.name for f in metadata.required_fields()] == ["required"]
    assert [f.name for f in metadata.optional_fields()] == ["optional"]


def test_empty_fields_partition_to_empty_tuples():
    metadata = ClassMetadata(owner=object, fields=(), qualified_name="Empty")
    assert metadata.field_names() == ()
    assert metadata.required_fields() == ()
    assert metadata.optional_fields() == ()
