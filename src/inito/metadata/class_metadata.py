"""Immutable, decoration-time snapshot of a class's field structure."""

from __future__ import annotations

from dataclasses import dataclass

from inito.metadata.field import FieldMetadata

METADATA_ATTRIBUTE = "__inito_metadata__"
"""Name of the class attribute used to cache a class's ClassMetadata."""


@dataclass(frozen=True)
class ClassMetadata:
    """Immutable, decoration-time snapshot of a class's field structure."""

    owner: type
    fields: tuple[FieldMetadata, ...]
    qualified_name: str

    def field_names(self) -> tuple[str, ...]:
        """Names of every declared field, in declaration order."""
        return tuple(field.name for field in self.fields)

    def required_fields(self) -> tuple[FieldMetadata, ...]:
        """Fields that have no default value or default factory."""
        return tuple(field for field in self.fields if field.is_required)

    def optional_fields(self) -> tuple[FieldMetadata, ...]:
        """Fields that have a default value or default factory."""
        return tuple(field for field in self.fields if not field.is_required)
