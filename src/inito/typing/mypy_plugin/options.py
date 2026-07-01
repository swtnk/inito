"""Reads keyword-argument decorator options (e.g. ``@Data(frozen=True)``).

inito's decorators are typed as plain ``Callable[..., Any]`` (built by
``make_decorator``), not a function with a real keyword signature, so the
CallableType-based argument lookup mypy's bundled attrs/dataclasses plugins
use doesn't apply here. Instead this reads the decorator call expression's
keyword arguments directly. Only the ``@Data(option=value, ...)`` call
style is supported for typing purposes - the alternative
``@Data(DataOptions(...))`` positional-instance style falls back to
defaults, since statically resolving an arbitrary options-instance
expression is out of scope for this plugin.
"""

from __future__ import annotations

from mypy.nodes import CallExpr, Expression
from mypy.plugin import ClassDefContext


def bool_option(ctx: ClassDefContext, name: str, default: bool) -> bool:
    """Return the keyword-argument bool value for name, or default."""
    expr = _keyword_argument(ctx, name)
    if expr is None:
        return default
    parsed = ctx.api.parse_bool(expr)
    return default if parsed is None else parsed


def str_option(ctx: ClassDefContext, name: str, default: str) -> str:
    """Return the keyword-argument string value for name, or default."""
    expr = _keyword_argument(ctx, name)
    if expr is None:
        return default
    parsed = ctx.api.parse_str_literal(expr)
    return default if parsed is None else parsed


def _keyword_argument(ctx: ClassDefContext, name: str) -> Expression | None:
    if not isinstance(ctx.reason, CallExpr):
        return None
    for arg_name, arg_expr in zip(ctx.reason.arg_names, ctx.reason.args):
        if arg_name == name:
            return arg_expr
    return None
