"""Generates a constructor accepting every declared field.

The rendering helpers are module-level functions (not private to
ConstructorGenerator) so future NoArgsConstructor/RequiredArgsConstructor
generators can reuse them without duplicating parameter/body rendering.

Field assignment uses a direct ``self.__dict__["x"] = x`` write for ordinary
(non-slotted) classes: it is ~2x faster than ``object.__setattr__`` and, by
bypassing ``__setattr__`` entirely, works in every stacking order with a
frozen dataclass or inito's own ``@Value``/``@Data(frozen=True)`` blocker
(construction writes straight to the instance dict; a post-construction
``obj.x = 5`` still goes through the blocking ``__setattr__`` and raises).
Fully slotted classes have no instance ``__dict__``, so they fall back to a
once-bound ``object.__setattr__`` (also faster than looking it up per field).
"""

from __future__ import annotations

from typing import Any

from inito.exceptions.errors import InvalidFieldDefinitionError
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata


class ConstructorGenerator:
    """Generates an __init__ accepting every declared field."""

    method_name = "__init__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __init__ source accepting every declared field."""
        use_dict = supports_dict_assignment(metadata.owner)
        parameters = render_parameter_list(metadata.fields)
        body = render_assignment_body(metadata.fields, use_dict)
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
        _add_setattr_global(metadata, globals_ns)
        return globals_ns


class NoArgsConstructorGenerator:
    """Generates a no-argument __init__ that assigns every field its default."""

    method_name = "__init__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return a no-argument __init__ using every field's default."""
        _require_all_fields_have_defaults(metadata)
        use_dict = supports_dict_assignment(metadata.owner)
        body = render_no_args_assignment_body(metadata.fields, use_dict)
        return f"def __init__(self):\n{body}\n"

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """Return the defaults and default factories the source references."""
        globals_ns: dict[str, Any] = {}
        for field in metadata.fields:
            if field.default_factory is not None:
                globals_ns[factory_name(field)] = field.default_factory
            else:
                globals_ns[default_name(field)] = field.default
        _add_setattr_global(metadata, globals_ns)
        return globals_ns


def _require_all_fields_have_defaults(metadata: ClassMetadata) -> None:
    required = metadata.required_fields()
    if not required:
        return
    names = ", ".join(field.name for field in required)
    raise InvalidFieldDefinitionError(
        f"@NoArgsConstructor requires every field to have a default; "
        f"{metadata.qualified_name!r} is missing defaults for: {names}."
    )


def render_no_args_assignment_body(fields: tuple[FieldMetadata, ...], use_dict: bool) -> str:
    """Render a no-argument __init__ body assigning every field its default."""
    if not fields:
        return "    pass"
    lines = _dict_prelude(use_dict)
    lines.extend(_render_no_args_assignment(field, use_dict) for field in fields)
    return "\n".join(lines)


def _render_no_args_assignment(field: FieldMetadata, use_dict: bool) -> str:
    if field.default_factory is not None:
        value_expr = f"{factory_name(field)}()"
    else:
        value_expr = default_name(field)
    return _assignment_line(field.name, value_expr, use_dict)


class RequiredArgsConstructorGenerator:
    """Generates an __init__ accepting only required fields; others get their default."""

    method_name = "__init__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return an __init__ accepting only required fields as parameters."""
        required, optional = metadata.required_fields(), metadata.optional_fields()
        parameters = ", ".join(field.name for field in required)
        header = f"def __init__(self{', ' + parameters if parameters else ''}):"
        body = render_required_args_assignment_body(
            required, optional, supports_dict_assignment(metadata.owner)
        )
        return f"{header}\n{body}\n"

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """Return the defaults and default factories the optional fields need."""
        globals_ns: dict[str, Any] = {}
        for field in metadata.optional_fields():
            if field.default_factory is not None:
                globals_ns[factory_name(field)] = field.default_factory
            else:
                globals_ns[default_name(field)] = field.default
        _add_setattr_global(metadata, globals_ns)
        return globals_ns


def render_required_args_assignment_body(
    required: tuple[FieldMetadata, ...], optional: tuple[FieldMetadata, ...], use_dict: bool
) -> str:
    """Render an __init__ body: required fields from parameters, others from defaults."""
    if not required and not optional:
        return "    pass"
    lines = _dict_prelude(use_dict)
    lines.extend(_assignment_line(field.name, field.name, use_dict) for field in required)
    lines.extend(_render_no_args_assignment(field, use_dict) for field in optional)
    return "\n".join(lines)


def render_parameter_list(fields: tuple[FieldMetadata, ...]) -> str:
    """Render the __init__ parameter list: required fields, then optional ones."""
    required = [field.name for field in fields if field.is_required]
    optional = [
        f"{field.name}={_default_reference(field)}" for field in fields if not field.is_required
    ]
    return ", ".join(required + optional)


def render_assignment_body(fields: tuple[FieldMetadata, ...], use_dict: bool) -> str:
    """Render the __init__ body assigning every field to self."""
    if not fields:
        return "    pass"
    lines = _dict_prelude(use_dict)
    lines.extend(_render_assignment(field, use_dict) for field in fields)
    return "\n".join(lines)


def _render_assignment(field: FieldMetadata, use_dict: bool) -> str:
    if field.default_factory is not None:
        sentinel = factory_sentinel_name(field)
        factory = factory_name(field)
        value_expr = f"{factory}() if {field.name} is {sentinel} else {field.name}"
    else:
        value_expr = field.name
    return _assignment_line(field.name, value_expr, use_dict)


def supports_dict_assignment(cls: type) -> bool:
    """Whether cls's instances expose a writable __dict__ (i.e. are not fully slotted).

    A ``__dict__`` write bypasses any ``__setattr__`` (a frozen dataclass's, or
    inito's own immutability blocker), so it is both faster than
    ``object.__setattr__`` and correct in every stacking order. Fully slotted
    classes have no instance ``__dict__`` and fall back to ``object.__setattr__``.
    """
    return cls.__dictoffset__ != 0


def _dict_prelude(use_dict: bool) -> list[str]:
    """The hoisted ``_d = self.__dict__`` line, once per constructor body."""
    return ["    _d = self.__dict__"] if use_dict else []


def _assignment_line(name: str, value_expr: str, use_dict: bool) -> str:
    if use_dict:
        return f'    _d["{name}"] = {value_expr}'
    return f'    _setattr(self, "{name}", {value_expr})'


def _add_setattr_global(metadata: ClassMetadata, globals_ns: dict[str, Any]) -> None:
    if not supports_dict_assignment(metadata.owner):
        globals_ns["_setattr"] = object.__setattr__


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
