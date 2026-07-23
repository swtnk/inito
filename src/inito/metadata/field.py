"""Immutable description of a single class field."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from inito.exceptions.errors import InvalidFieldDefinitionError

MISSING = object()
"""Sentinel marking the absence of a default value or default factory."""

RESERVED_FIELD_PREFIX = "_inito_"
"""Reserved prefix: every codegen-internal global uses it, so a field name that
starts with it is rejected to guarantee a field can never shadow one."""


@dataclass(frozen=True)
class FieldSpec:
    """A field default declared explicitly via :func:`field`, read at extraction."""

    default: Any = MISSING
    default_factory: Callable[[], Any] | None = None


def field(*, default: object = MISSING, default_factory: Callable[[], Any] | None = None) -> Any:  # noqa: ANN401 -- Any return so the annotated field type still checks
    """Declare a field's default explicitly, e.g. a per-instance ``default_factory``.

    The inito-native equivalent of :func:`dataclasses.field`: a mutable default
    such as ``items: list = []`` is rejected (one object would be shared across
    every instance), so declare it as
    ``items: list = field(default_factory=list)`` to build a fresh one per
    instance. Returns ``Any`` so the annotated field type still type-checks.
    """
    if default is not MISSING and default_factory is not None:
        raise InvalidFieldDefinitionError("field() cannot take both default and default_factory.")
    return FieldSpec(default=default, default_factory=default_factory)


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
