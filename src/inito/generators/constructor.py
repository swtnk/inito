"""Generates a constructor accepting every declared field.

The rendering helpers are module-level functions (not private to
ConstructorGenerator) so future NoArgsConstructor/RequiredArgsConstructor
generators can reuse them without duplicating parameter/body rendering.
"""

from __future__ import annotations

from typing import Any

from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


class ConstructorGenerator:
    """Generates an __init__ accepting every declared field."""

    method_name = "__init__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __init__ source accepting every declared field."""
        parameters = render_parameter_list(metadata.fields)
        body = render_assignment_body(metadata.fields)
        header = f"def __init__(self{', ' + parameters if parameters else ''}):"
        return f"{header}\n{body}\n"

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """Return the defaults and default factories the source references."""
        globals_ns: dict[str, Any] = {}
        for field in metadata.fields:
            if field.default_factory is not None:
                globals_ns[factory_name(field)] = field.default_factory
                globals_ns[factory_sentinel_name(field)] = object()
            elif field.has_default:
                globals_ns[default_name(field)] = field.default
        return globals_ns


def render_parameter_list(fields: tuple[FieldMetadata, ...]) -> str:
    """Render the __init__ parameter list: required fields, then optional ones."""
    required = [field.name for field in fields if field.is_required]
    optional = [
        f"{field.name}={_default_reference(field)}" for field in fields if not field.is_required
    ]
    return ", ".join(required + optional)


def render_assignment_body(fields: tuple[FieldMetadata, ...]) -> str:
    """Render the __init__ body assigning every field to self."""
    if not fields:
        return "    pass"
    return "\n".join(_render_assignment(field) for field in fields)


def _render_assignment(field: FieldMetadata) -> str:
    if field.default_factory is not None:
        sentinel = factory_sentinel_name(field)
        factory = factory_name(field)
        return (
            f"    self.{field.name} = {factory}() if {field.name} is {sentinel} else {field.name}"
        )
    return f"    self.{field.name} = {field.name}"


def _default_reference(field: FieldMetadata) -> str:
    if field.default_factory is not None:
        return factory_sentinel_name(field)
    return default_name(field)


def default_name(field: FieldMetadata) -> str:
    """Name of the global variable holding field's default value."""
    return f"_default_{field.name}"


def factory_name(field: FieldMetadata) -> str:
    """Name of the global variable holding field's default factory."""
    return f"_factory_{field.name}"


def factory_sentinel_name(field: FieldMetadata) -> str:
    """Name of the global sentinel marking 'call the default factory'."""
    return f"_factory_sentinel_{field.name}"
