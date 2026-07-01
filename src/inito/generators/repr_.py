"""Generates a __repr__ listing every declared field."""

from __future__ import annotations

from typing import Any

from inito.metadata.class_metadata import ClassMetadata


class ReprGenerator:
    """Generates a __repr__ listing every declared field."""

    method_name = "__repr__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __repr__ source rendering every declared field."""
        class_name = metadata.owner.__name__
        parts = ", ".join(f"{name}={{self.{name}!r}}" for name in metadata.field_names())
        return f'def __repr__(self):\n    return f"{class_name}({parts})"\n'

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """__repr__ needs no globals beyond self."""
        return {}
