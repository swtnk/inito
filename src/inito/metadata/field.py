"""Immutable description of a single class field."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

MISSING = object()
"""Sentinel marking the absence of a default value or default factory."""


@dataclass(frozen=True)
class FieldMetadata:
    """Immutable description of a single class field."""

    name: str
    type_hint: Any
    default: Any = MISSING
    default_factory: Callable[[], Any] | None = None

    @property
    def has_default(self) -> bool:
        """Whether the field has a plain default value."""
        return self.default is not MISSING

    @property
    def is_required(self) -> bool:
        """Whether the field must be supplied by the caller."""
        return not self.has_default and self.default_factory is None
