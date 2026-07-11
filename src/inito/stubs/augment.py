"""Inject inito's generated members into a stubgen-produced ``.pyi``.

stubgen sees only the source, so a decorated class's ``.pyi`` lacks the members
inito attaches at runtime. This parses that stub, and for every top-level class
whose runtime object carries inito metadata, strips inito's own class decorators
(so pyright doesn't double-synthesize via ``dataclass_transform``) and injects
the generated members from ``emit``.
"""

from __future__ import annotations

import ast
from types import ModuleType

from inito.metadata.class_metadata import METADATA_ATTRIBUTE
from inito.stubs.emit import member_stub_source

_INITO_DECORATORS = frozenset(
    {
        "Data",
        "data",
        "Value",
        "value",
        "Getter",
        "getter",
        "Setter",
        "setter",
        "ToString",
        "to_string",
        "EqualsAndHashCode",
        "equals_and_hash_code",
        "NoArgsConstructor",
        "no_args_constructor",
        "AllArgsConstructor",
        "all_args_constructor",
        "RequiredArgsConstructor",
        "required_args_constructor",
        "Builder",
        "builder",
        "Config",
        "config",
    }
)


def augment_stub(stub_source: str, module: ModuleType) -> str:
    """Return stub_source with inito's generated members injected into its classes."""
    tree = ast.parse(stub_source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        cls = getattr(module, node.name, None)
        if not isinstance(cls, type) or METADATA_ATTRIBUTE not in cls.__dict__:
            continue
        members = member_stub_source(cls)
        if not members:
            continue
        node.decorator_list = [d for d in node.decorator_list if not _is_inito_decorator(d)]
        _inject(node, ast.parse(members).body)
    _ensure_any_import(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def _ensure_any_import(tree: ast.Module) -> None:
    """Add `from typing import Any` if a generated member references Any and it isn't imported."""
    if "Any" not in {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}:
        return
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "typing"
            and any(alias.name == "Any" for alias in node.names)
        ):
            return
    tree.body.insert(0, ast.ImportFrom(module="typing", names=[ast.alias(name="Any")], level=0))


def _decorator_name(node: ast.expr) -> str | None:
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _is_inito_decorator(node: ast.expr) -> bool:
    return _decorator_name(node) in _INITO_DECORATORS


def _member_name(node: ast.stmt) -> str | None:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    return None


def _is_ellipsis(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and node.value.value is Ellipsis
    )


def _inject(class_node: ast.ClassDef, members: list[ast.stmt]) -> None:
    injected = {name for node in members if (name := _member_name(node)) is not None}
    # Drop stubgen's `...` placeholder body and any member we are replacing.
    body = [
        stmt
        for stmt in class_node.body
        if not _is_ellipsis(stmt) and _member_name(stmt) not in injected
    ]
    class_node.body = body + members
