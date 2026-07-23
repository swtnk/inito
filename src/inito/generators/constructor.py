"""Generates a constructor accepting every declared field.

The rendering helpers are module-level functions (not private to
ConstructorGenerator) so future NoArgsConstructor/RequiredArgsConstructor
generators can reuse them without duplicating parameter/body rendering.

Field assignment uses plain ``self.x = x`` for ordinary (non-frozen) classes:
it is the fastest construction *and* keeps CPython's key-sharing instance
dict (PEP 412) intact, so attribute reads and ``__eq__``/``__hash__``/
``__repr__`` stay at handwritten speed. When the class already blocks
``__setattr__`` (inito's own ``@Value``/``@Data(frozen=True)``, whose
immutability is attached *before* the constructor, or a stacked
``@dataclass(frozen=True)`` underneath), fields are assigned via a
once-bound ``object.__setattr__`` instead - still key-sharing-friendly (so
reads stay fast), just bypassing the blocking ``__setattr__`` for
construction. A ``__dict__`` subscript write is deliberately *not* used: it
would be a hair faster to construct but permanently de-optimizes every
attribute read on the instance.
"""

from __future__ import annotations

from typing import Any

from inito.exceptions.errors import InvalidFieldDefinitionError
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import RESERVED_FIELD_PREFIX, FieldMetadata
from inito.utils.freezing import freeze_value


class ConstructorGenerator:
    """Generates an __init__ accepting every declared field.

    ``freeze_collections`` wraps each assigned value in ``freeze_value`` so a
    mutable collection is stored as an immutable one - used by
    ``@Value(freeze_collections=True)``.
    """

    method_name = "__init__"

    def __init__(self, freeze_collections: bool = False) -> None:
        """Store whether assigned collection values are frozen at construction."""
        self.freeze_collections = freeze_collections

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the __init__ source accepting every declared field."""
        _reject_required_after_optional(metadata)
        use_setattr = needs_object_setattr(metadata.owner)
        parameters = render_parameter_list(metadata.fields)
        body = render_assignment_body(metadata.fields, use_setattr, self.freeze_collections)
        header = f"def __init__(self{', ' + parameters if parameters else ''}):"
        return f"{header}\n{body}\n{render_post_init_call(metadata)}"

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
        if self.freeze_collections:
            globals_ns[_FREEZE_GLOBAL] = freeze_value
        return globals_ns


class NoArgsConstructorGenerator:
    """Generates a no-argument __init__ that assigns every field its default."""

    method_name = "__init__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return a no-argument __init__ using every field's default."""
        _require_all_fields_have_defaults(metadata)
        use_setattr = needs_object_setattr(metadata.owner)
        body = render_no_args_assignment_body(metadata.fields, use_setattr)
        return f"def __init__(self):\n{body}\n{render_post_init_call(metadata)}"

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


def render_no_args_assignment_body(fields: tuple[FieldMetadata, ...], use_setattr: bool) -> str:
    """Render a no-argument __init__ body assigning every field its default."""
    if not fields:
        return "    pass"
    return "\n".join(_render_no_args_assignment(field, use_setattr) for field in fields)


def _render_no_args_assignment(field: FieldMetadata, use_setattr: bool) -> str:
    if field.default_factory is not None:
        value_expr = f"{factory_name(field)}()"
    else:
        value_expr = default_name(field)
    return _assignment_line(field.name, value_expr, use_setattr)


class RequiredArgsConstructorGenerator:
    """Generates an __init__ accepting only required fields; others get their default."""

    method_name = "__init__"

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return an __init__ accepting only required fields as parameters."""
        required, optional = metadata.required_fields(), metadata.optional_fields()
        parameters = ", ".join(field.name for field in required)
        header = f"def __init__(self{', ' + parameters if parameters else ''}):"
        body = render_required_args_assignment_body(
            required, optional, needs_object_setattr(metadata.owner)
        )
        return f"{header}\n{body}\n{render_post_init_call(metadata)}"

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
    required: tuple[FieldMetadata, ...], optional: tuple[FieldMetadata, ...], use_setattr: bool
) -> str:
    """Render an __init__ body: required fields from parameters, others from defaults."""
    lines = [_assignment_line(field.name, field.name, use_setattr) for field in required]
    lines.extend(_render_no_args_assignment(field, use_setattr) for field in optional)
    return "\n".join(lines) if lines else "    pass"


POST_INIT_METHOD = "__post_init__"
"""The user hook a generated constructor calls after assigning every field."""


def has_post_init(cls: type) -> bool:
    """Whether cls (or a base) defines the ``__post_init__`` invariant hook."""
    return hasattr(cls, POST_INIT_METHOD)


def render_post_init_call(metadata: ClassMetadata) -> str:
    """Render the trailing ``self.__post_init__()`` line, or nothing if absent."""
    if has_post_init(metadata.owner):
        return f"    self.{POST_INIT_METHOD}()\n"
    return ""


def render_parameter_list(fields: tuple[FieldMetadata, ...]) -> str:
    """Render the __init__ parameter list in declaration order.

    Order is preserved so positional construction maps arguments to the fields
    the reader declared. ``_reject_required_after_optional`` has already ensured
    no required field follows an optional one, so this stays valid Python.
    """
    return ", ".join(
        field.name if field.is_required else f"{field.name}={_default_reference(field)}"
        for field in fields
    )


def _reject_required_after_optional(metadata: ClassMetadata) -> None:
    optional_before: str | None = None
    for field in metadata.fields:
        if not field.is_required:
            optional_before = field.name
        elif optional_before is not None:
            raise InvalidFieldDefinitionError(
                f"{metadata.qualified_name!r} declares required field "
                f"{field.name!r} after field {optional_before!r}, which has a "
                f"default; a required field cannot follow a defaulted one. "
                f"Reorder the fields, or give {field.name!r} a default too."
            )


def render_assignment_body(
    fields: tuple[FieldMetadata, ...], use_setattr: bool, freeze: bool = False
) -> str:
    """Render the __init__ body assigning every field to self."""
    if not fields:
        return "    pass"
    return "\n".join(_render_assignment(field, use_setattr, freeze) for field in fields)


def _render_assignment(field: FieldMetadata, use_setattr: bool, freeze: bool = False) -> str:
    if field.default_factory is not None:
        sentinel = factory_sentinel_name(field)
        factory = factory_name(field)
        value_expr = f"{factory}() if {field.name} is {sentinel} else {field.name}"
    else:
        value_expr = field.name
    if freeze:
        value_expr = f"{_FREEZE_GLOBAL}({value_expr})"
    return _assignment_line(field.name, value_expr, use_setattr)


def needs_object_setattr(cls: type) -> bool:
    """Whether cls overrides ``__setattr__`` and so needs ``object.__setattr__``.

    True for inito's own immutable classes (``@Value``/``@Data(frozen=True)``,
    which attach their blocking ``__setattr__`` before the constructor) and for
    a class stacked on top of ``@dataclass(frozen=True)``. False for an ordinary
    class, where a plain ``self.x = x`` is both fastest and key-sharing-friendly.
    Walks the MRO (excluding ``object``) rather than an identity check so an
    inherited blocking ``__setattr__`` is also detected.
    """
    return any("__setattr__" in klass.__dict__ for klass in cls.__mro__[:-1])


_SETATTR_GLOBAL = f"{RESERVED_FIELD_PREFIX}setattr"
_FREEZE_GLOBAL = f"{RESERVED_FIELD_PREFIX}freeze"


def _assignment_line(name: str, value_expr: str, use_setattr: bool) -> str:
    if use_setattr:
        return f'    {_SETATTR_GLOBAL}(self, "{name}", {value_expr})'
    return f"    self.{name} = {value_expr}"


def _add_setattr_global(metadata: ClassMetadata, globals_ns: dict[str, Any]) -> None:
    if needs_object_setattr(metadata.owner):
        globals_ns[_SETATTR_GLOBAL] = object.__setattr__


def _default_reference(field: FieldMetadata) -> str:
    if field.default_factory is not None:
        return factory_sentinel_name(field)
    return default_name(field)


def default_name(field: FieldMetadata) -> str:
    """Name of the global variable holding field's default value."""
    return f"{RESERVED_FIELD_PREFIX}default_{field.name}"


def factory_name(field: FieldMetadata) -> str:
    """Name of the global variable holding field's default factory."""
    return f"{RESERVED_FIELD_PREFIX}factory_{field.name}"


def factory_sentinel_name(field: FieldMetadata) -> str:
    """Name of the global sentinel marking 'call the default factory'."""
    return f"{RESERVED_FIELD_PREFIX}factory_sentinel_{field.name}"
