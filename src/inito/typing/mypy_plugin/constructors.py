"""Synthesizes __init__ and get_/set_ accessors for the constructor decorators.

Covers @Data, @Getter, @Setter, @NoArgsConstructor, @AllArgsConstructor,
and @RequiredArgsConstructor.
"""

from __future__ import annotations

from mypy.nodes import ARG_OPT, ARG_POS, Argument, Var
from mypy.plugin import ClassDefContext
from mypy.plugins.common import add_method_to_class
from mypy.types import NoneType

from inito.typing.mypy_plugin.fields import InitoField, collect_fields
from inito.typing.mypy_plugin.options import bool_option, str_option


def transform_data(ctx: ClassDefContext) -> bool:
    """Synthesize @Data's __init__ and (per options) get_/set_ accessors."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    frozen = bool_option(ctx, "frozen", False)
    include_getters = bool_option(ctx, "include_getters", True)
    include_setters = bool_option(ctx, "include_setters", True)
    accessors = str_option(ctx, "accessors", "lombok") != "attr"

    add_init(ctx, fields)
    if accessors and include_getters:
        add_getters(ctx, fields)
    if accessors and include_setters and not frozen:
        add_setters(ctx, fields)
    _apply_slots(ctx, fields)
    return True


def transform_getter(ctx: ClassDefContext) -> bool:
    """Synthesize @Getter's get_<field>() accessors."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    add_getters(ctx, fields)
    return True


def transform_setter(ctx: ClassDefContext) -> bool:
    """Synthesize @Setter's set_<field>(value) accessors."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    add_setters(ctx, fields)
    return True


def transform_no_args_constructor(ctx: ClassDefContext) -> bool:
    """Synthesize @NoArgsConstructor's no-argument __init__."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    missing = [field.name for field in fields if not field.has_default]
    if missing:
        ctx.api.fail(
            "@NoArgsConstructor requires every field to have a default; "
            f"missing defaults for: {', '.join(missing)}",
            ctx.cls,
        )
    add_method_to_class(ctx.api, ctx.cls, "__init__", args=[], return_type=NoneType())
    return True


def transform_all_args_constructor(ctx: ClassDefContext) -> bool:
    """Synthesize @AllArgsConstructor's __init__ accepting every field."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    add_init(ctx, fields)
    return True


def transform_required_args_constructor(ctx: ClassDefContext) -> bool:
    """Synthesize @RequiredArgsConstructor's __init__ accepting only required fields."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    add_init(ctx, [field for field in fields if not field.has_default])
    return True


def transform_value(ctx: ClassDefContext) -> bool:
    """Synthesize @Value's __init__ and (per options) get_<field>() accessors."""
    fields = collect_fields(ctx)
    if fields is None:  # pragma: no cover -- mypy deferral guard (unresolved field type)
        return False
    include_getters = bool_option(ctx, "include_getters", True)

    add_init(ctx, fields)
    if include_getters:
        add_getters(ctx, fields)
    _apply_slots(ctx, fields)
    return True


def add_init(ctx: ClassDefContext, fields: list[InitoField]) -> None:
    """Add an __init__ accepting fields in declaration order, matching the runtime.

    Reports the same error the runtime raises when a required field follows a
    defaulted one, since that can't form a valid positional signature.
    """
    _fail_on_required_after_optional(ctx, fields)
    args = [
        Argument(
            Var(field.name, field.type),
            field.type,
            None,
            ARG_OPT if field.has_default else ARG_POS,
        )
        for field in fields
    ]
    add_method_to_class(ctx.api, ctx.cls, "__init__", args=args, return_type=NoneType())


def _fail_on_required_after_optional(ctx: ClassDefContext, fields: list[InitoField]) -> None:
    optional_before: str | None = None
    for field in fields:
        if field.has_default:
            optional_before = field.name
        elif optional_before is not None:
            ctx.api.fail(
                f"Required field {field.name!r} cannot follow defaulted field "
                f"{optional_before!r}; reorder the fields or give it a default.",
                ctx.cls,
            )
            return


def _apply_slots(ctx: ClassDefContext, fields: list[InitoField]) -> None:
    if bool_option(ctx, "slots", False):
        ctx.cls.info.slots = {field.name for field in fields}


def add_getters(ctx: ClassDefContext, fields: list[InitoField]) -> None:
    """Add a get_<field>() method for each field."""
    for field in fields:
        add_method_to_class(ctx.api, ctx.cls, f"get_{field.name}", args=[], return_type=field.type)


def add_setters(ctx: ClassDefContext, fields: list[InitoField]) -> None:
    """Add a set_<field>(value) method for each field."""
    for field in fields:
        args = [Argument(Var("value", field.type), field.type, None, ARG_POS)]
        add_method_to_class(
            ctx.api, ctx.cls, f"set_{field.name}", args=args, return_type=NoneType()
        )
