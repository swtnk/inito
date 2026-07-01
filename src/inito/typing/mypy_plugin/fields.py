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
    NameExpr,
    PlaceholderNode,
    TempNode,
    TypeAlias,
    TypeInfo,
    Var,
)
from mypy.plugin import ClassDefContext
from mypy.types import Type


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
        if fields is None:
            return None
        found.update(fields)

    current = _own_fields(ctx.cls.info, body=ctx.cls.defs)
    if current is None:
        return None
    found.update(current)

    return list(found.values())


def _own_fields(info: TypeInfo, body: Block | None = None) -> dict[str, InitoField] | None:
    """Return the fields declared directly in info's own class body."""
    fields: dict[str, InitoField] = {}
    for stmt in _assignment_statements(body if body is not None else info.defn.defs):
        if not stmt.new_syntax:
            continue
        lvalue = stmt.lvalues[0]
        if not isinstance(lvalue, NameExpr):
            continue

        sym = info.names.get(lvalue.name)
        if sym is None:
            continue
        node = sym.node
        if isinstance(node, PlaceholderNode):
            return None
        if isinstance(node, (TypeAlias, Decorator)):
            continue
        if not isinstance(node, Var) or node.is_classvar:
            continue
        if node.type is None:
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
