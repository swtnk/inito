"""Class field metadata extraction, built once at decoration time."""

from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.extractor import MetadataExtractor, default_extractor
from inito.metadata.field import MISSING, FieldMetadata

__all__ = [
    "MISSING",
    "ClassMetadata",
    "FieldMetadata",
    "MetadataExtractor",
    "default_extractor",
]
