"""Generates a __repr__ listing every declared field."""

from __future__ import annotations

from typing import Any

from inito.metadata.class_metadata import ClassMetadata


class ReprGenerator:
    """Generates a __repr__ listing every declared field."""

    method_name = "__repr__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __repr__ source rendering every declared field.

        The class name is referenced through a ``_cls_name`` global rather than
        interpolated into the source text: a class built dynamically (e.g. by a
        framework metaclass via ``type(name, ...)``) can carry an arbitrary
        ``__name__`` string, and baking that into ``exec``'d source would let an
        unusual name break compilation or inject statements. Field names come
        from real annotations and are always identifiers, so they stay inline.
        """
        parts = ", ".join(f"{name}={{self.{name}!r}}" for name in metadata.field_names())
        return f'def __repr__(self):\n    return f"{{_cls_name}}({parts})"\n'

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """Provide the class name the generated f-string references."""
        return {"_cls_name": metadata.owner.__name__}
