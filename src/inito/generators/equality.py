"""Generates __eq__ and __hash__ over every declared field.

Kept in one module deliberately: Python's data model couples the two
(defining __eq__ without __hash__ implicitly sets __hash__ to None), and
@Data always attaches both together, matching Lombok's equals+hashCode pairing.
"""

from __future__ import annotations

from typing import Any

from inito.metadata.class_metadata import ClassMetadata


class EqGenerator:
    """Generates an __eq__ comparing all declared fields."""

    method_name = "__eq__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __eq__ source comparing every declared field."""
        names = metadata.field_names()
        self_tuple = _tuple_expression(names, "self")
        other_tuple = _tuple_expression(names, "other")
        return (
            "def __eq__(self, other):\n"
            "    if other.__class__ is not self.__class__:\n"
            "        return NotImplemented\n"
            f"    return {self_tuple} == {other_tuple}\n"
        )

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """__eq__ needs no globals beyond self and other."""
        return {}


class HashGenerator:
    """Generates a __hash__ over all declared fields."""

    method_name = "__hash__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __hash__ source hashing every declared field."""
        self_tuple = _tuple_expression(metadata.field_names(), "self")
        return f"def __hash__(self):\n    return hash({self_tuple})\n"

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """__hash__ needs no globals beyond self."""
        return {}


def _tuple_expression(names: tuple[str, ...], owner: str) -> str:
    if not names:
        return "()"
    items = ", ".join(f"{owner}.{name}" for name in names)
    return f"({items},)"
