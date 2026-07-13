"""Synthesizes @Jsonize's ``to_dict``/``to_json`` for mypy."""

from __future__ import annotations

from mypy.nodes import ARG_STAR2, Argument, Var
from mypy.plugin import ClassDefContext
from mypy.plugins.common import add_method_to_class
from mypy.types import AnyType, TypeOfAny


def transform_jsonize(ctx: ClassDefContext) -> bool:
    """Add ``to_dict(self) -> dict[str, Any]`` and ``to_json(self, **kwargs) -> str``."""
    api = ctx.api
    any_type = AnyType(TypeOfAny.special_form)
    str_type = api.named_type("builtins.str")
    add_method_to_class(
        api,
        ctx.cls,
        "to_dict",
        args=[],
        return_type=api.named_type("builtins.dict", [str_type, any_type]),
    )
    kwargs = Argument(Var("kwargs", any_type), any_type, None, ARG_STAR2)
    add_method_to_class(api, ctx.cls, "to_json", args=[kwargs], return_type=str_type)
    return True
