"""Synthesizes @Builder's nested Builder class, builder(), and to_builder().

The nested Builder class is built as a genuine synthetic TypeInfo (the same
technique mypy's own attrs plugin uses for its internal magic-attribute
class), with real fluent setter methods and a build() method attached via
the same add_method_to_class helper used for ordinary methods.
"""

from __future__ import annotations

from mypy.nodes import ARG_POS, MDEF, Argument, SymbolTableNode, Var
from mypy.plugin import ClassDefContext
from mypy.plugins.common import add_method_to_class
from mypy.types import NoneType
from mypy.typevars import fill_typevars

from inito.typing.mypy_plugin.fields import collect_fields
from inito.typing.mypy_plugin.options import bool_option, str_option


def transform_builder(ctx: ClassDefContext) -> bool:
    """Synthesize the Builder nested class, builder(), and optional to_builder()."""
    fields = collect_fields(ctx)
    if fields is None:
        return False

    setter_prefix = str_option(ctx, "setter_prefix", "")
    build_method_name = str_option(ctx, "build_method_name", "build")
    to_builder = bool_option(ctx, "to_builder", False)

    object_type = ctx.api.named_type("builtins.object")
    builder_info = ctx.api.basic_new_typeinfo("Builder", object_type, ctx.cls.info.line)
    builder_info._fullname = f"{ctx.cls.info.fullname}.Builder"
    builder_info.defn.fullname = builder_info._fullname
    builder_self_type = fill_typevars(builder_info)
    owner_type = fill_typevars(ctx.cls.info)

    add_method_to_class(ctx.api, builder_info.defn, "__init__", args=[], return_type=NoneType())
    for field in fields:
        args = [Argument(Var("value", field.type), field.type, None, ARG_POS)]
        add_method_to_class(
            ctx.api,
            builder_info.defn,
            f"{setter_prefix}{field.name}",
            args=args,
            return_type=builder_self_type,
        )
    add_method_to_class(
        ctx.api, builder_info.defn, build_method_name, args=[], return_type=owner_type
    )

    ctx.cls.info.names["Builder"] = SymbolTableNode(MDEF, builder_info, plugin_generated=True)
    add_method_to_class(
        ctx.api, ctx.cls, "builder", args=[], return_type=builder_self_type, is_classmethod=True
    )
    if to_builder:
        add_method_to_class(ctx.api, ctx.cls, "to_builder", args=[], return_type=builder_self_type)

    return True
