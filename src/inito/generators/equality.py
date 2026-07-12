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
        """Return the __eq__ source comparing every declared field.

        Emits a field-by-field ``and``-chain (``self.a == other.a and ...``)
        rather than comparing two tuples: it allocates nothing per call and
        short-circuits on the first differing field (the common case in set/dict
        membership), so it is faster than the tuple form dataclasses generate.
        """
        return (
            "def __eq__(self, other):\n"
            "    if other.__class__ is not self.__class__:\n"
            "        return NotImplemented\n"
            f"    return {_equality_expression(metadata.field_names())}\n"
        )

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """__eq__ needs no globals beyond self and other."""
        return {}


class HashGenerator:
    """Generates a __hash__ over all declared fields."""

    method_name = "__hash__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __hash__ source hashing every declared field.

        A single-field class hashes the field directly (``hash(self.a)``) instead
        of wrapping it in a one-element tuple — still consistent with ``__eq__``,
        but without the per-call tuple allocation. Multi-field classes hash a
        tuple of every field, as usual.
        """
        return f"def __hash__(self):\n    return hash({_hash_argument(metadata.field_names())})\n"

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """__hash__ needs no globals beyond self."""
        return {}


def _equality_expression(names: tuple[str, ...]) -> str:
    if not names:
        return "True"
    return " and ".join(f"self.{name} == other.{name}" for name in names)


def _hash_argument(names: tuple[str, ...]) -> str:
    if len(names) == 1:
        return f"self.{names[0]}"
    return _tuple_expression(names, "self")


def _tuple_expression(names: tuple[str, ...], owner: str) -> str:
    if not names:
        return "()"
    items = ", ".join(f"{owner}.{name}" for name in names)
    return f"({items},)"
