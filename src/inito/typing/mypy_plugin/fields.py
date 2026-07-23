"""Collects declared fields from a class and its bases for the mypy plugin.

Mirrors ``inito.reflection.introspection``'s runtime MRO-walk exactly, but
over mypy's semantic-analysis AST instead of real `__annotations__` - so a
field declared on any ancestor (inito-decorated or not) is picked up, with a
subclass's own declaration overriding a base's at the same position.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from mypy.nodes import (
    AssignmentStmt,
    Block,
    Decorator,
    DictExpr,
    ListExpr,
    NameExpr,
    PlaceholderNode,
    SetExpr,
    TempNode,
    TypeAlias,
    TypeInfo,
    Var,
)
from mypy.plugin import ClassDefContext
from mypy.types import Type

_MUTABLE_LITERALS = (ListExpr, DictExpr, SetExpr)


@dataclass(frozen=True)
class InitoField:
    """A single field's name, static type, and whether it has a default."""

    name: str
    type: Type
    has_default: bool


def collect_fields(ctx: ClassDefContext) -> list[InitoField] | None:
    """Return every field declared on ctx.cls or an ancestor, in MRO order.

    Returns None if some field's type isn't ready yet (the caller should
    return False from its class_decorator_hook_2 to request another pass).
    """
    found: dict[str, InitoField] = {}
    for info in reversed(ctx.cls.info.mro[1:-1]):
        fields = _own_fields(info)
        if fields is None:  # pragma: no cover -- placeholder/unresolved base, retried by mypy
            return None
        found.update(fields)

    current = _own_fields(ctx.cls.info, body=ctx.cls.defs)
    if current is None:  # pragma: no cover -- placeholder/unresolved field, retried by mypy
        return None
    found.update(current)

    report_mutable_defaults(ctx)
    return list(found.values())


def report_mutable_defaults(ctx: ClassDefContext) -> None:
    """Flag a mutable literal default (``= []``/``{}``/``{...}``), as the runtime does."""
    for stmt in _assignment_statements(ctx.cls.defs):
        if stmt.new_syntax and isinstance(stmt.rvalue, _MUTABLE_LITERALS):
            name = stmt.lvalues[0]
            label = name.name if isinstance(name, NameExpr) else "field"
            ctx.api.fail(
                f"Mutable default for {label!r} is shared across instances; "
                f"use field(default_factory=...) from inito.",
                stmt,
            )


def _own_fields(info: TypeInfo, body: Block | None = None) -> dict[str, InitoField] | None:
    """Return the fields declared directly in info's own class body."""
    fields: dict[str, InitoField] = {}
    for stmt in _assignment_statements(body if body is not None else info.defn.defs):
        if not stmt.new_syntax:
            continue
        lvalue = stmt.lvalues[0]
        if not isinstance(lvalue, NameExpr):  # pragma: no cover -- non-name assignment target
            continue

        sym = info.names.get(lvalue.name)
        if sym is None:  # pragma: no cover -- symbol not yet bound in this pass
            continue
        node = sym.node
        if isinstance(
            node, PlaceholderNode
        ):  # pragma: no cover -- unresolved node, retried by mypy
            return None
        if isinstance(node, (TypeAlias, Decorator)):  # pragma: no cover -- not a field declaration
            continue
        if not isinstance(node, Var) or node.is_classvar:
            continue
        if node.type is None:  # pragma: no cover -- untyped var, resolved on a later pass
            return None

        fields[lvalue.name] = InitoField(
            name=lvalue.name,
            type=node.type,
            has_default=not isinstance(stmt.rvalue, TempNode),
        )
    return fields


def _assignment_statements(block: Block) -> Iterator[AssignmentStmt]:
    for stmt in block.body:
        if isinstance(stmt, AssignmentStmt):
            yield stmt
