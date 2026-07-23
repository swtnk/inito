"""Shallow, construction-time coercion of mutable collections to immutable ones.

Used by ``@Value(freeze_collections=True)``: a ``list`` becomes a ``tuple``, a
``set`` a ``frozenset``, and a ``dict`` a read-only ``MappingProxyType``. Shallow
by design (nested containers are left as-is) - deep freezing is slower and rarely
what is wanted. Anything else is returned unchanged.
"""

from __future__ import annotations

from types import MappingProxyType


def freeze_value(value: object) -> object:
    """Return an immutable view of a top-level mutable collection, else value."""
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, set):
        return frozenset(value)
    if isinstance(value, dict):
        return MappingProxyType(dict(value))
    return value
