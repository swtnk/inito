"""Emit ``.pyi`` member declarations for a class's inito-generated members.

The generated members are real, marked attributes on the decorated class
(``core.attach`` stamps ``_inito_generated``); their field types come from the
cached ``ClassMetadata``. This module turns those into stub source that
``augment`` injects into the class body, so pyright sees every generated member.
"""

from __future__ import annotations

import inspect
from typing import Any

from inito.core.attach import GENERATED_MARKER
from inito.metadata.class_metadata import METADATA_ATTRIBUTE


def _is_generated(obj: Any) -> bool:  # noqa: ANN401 -- inspects an arbitrary class member
    return getattr(obj, GENERATED_MARKER, False) is True


def _type_str(type_hint: Any) -> str:  # noqa: ANN401 -- arbitrary resolved annotation
    if isinstance(type_hint, type):
        return type_hint.__qualname__
    return str(type_hint).replace("typing.", "")


def member_stub_source(cls: type) -> str:
    """Return stub source for cls's generated members, or '' if it has none."""
    metadata = cls.__dict__.get(METADATA_ATTRIBUTE)
    if metadata is None:
        return ""
    field_types = {field.name: _type_str(field.type_hint) for field in metadata.fields}
    owner = cls.__name__
    blocks: list[str] = []
    for name, obj in cls.__dict__.items():
        if isinstance(obj, classmethod) and _is_generated(obj.__func__):
            blocks.append(f"@classmethod\ndef {name}(cls) -> {owner}.Builder: ...")
        elif isinstance(obj, type) and _is_generated(obj):
            blocks.append(_builder_class_source(owner, obj, field_types))
        elif inspect.isfunction(obj) and _is_generated(obj):
            blocks.append(_method_source(owner, name, obj, field_types))
    return "\n".join(block for block in blocks if block)


def _method_source(owner: str, name: str, fn: Any, field_types: dict[str, str]) -> str:  # noqa: ANN401
    if name == "__init__":
        return _init_source(fn, field_types)
    if name == "__repr__":
        return "def __repr__(self) -> str: ..."
    if name == "__eq__":
        return "def __eq__(self, other: object) -> bool: ..."
    if name == "__hash__":
        return "def __hash__(self) -> int: ..."
    if name == "__setattr__":
        return "def __setattr__(self, name: str, value: object) -> None: ..."
    if name == "__delattr__":
        return "def __delattr__(self, name: str) -> None: ..."
    if name == "to_builder":
        return f"def to_builder(self) -> {owner}.Builder: ..."
    if name.startswith("get_"):
        return f"def {name}(self) -> {field_types.get(name[4:], 'Any')}: ..."
    if name.startswith("set_"):
        return f"def {name}(self, value: {field_types.get(name[4:], 'Any')}) -> None: ..."
    return f"def {name}(self, *args: Any, **kwargs: Any) -> Any: ..."


def _init_source(fn: Any, field_types: dict[str, str]) -> str:  # noqa: ANN401
    params = []
    for pname, param in inspect.signature(fn).parameters.items():
        if pname == "self":
            continue
        annotation = field_types.get(pname, "Any")
        suffix = "" if param.default is inspect.Parameter.empty else " = ..."
        params.append(f"{pname}: {annotation}{suffix}")
    inner = (", " + ", ".join(params)) if params else ""
    return f"def __init__(self{inner}) -> None: ..."


def _builder_class_source(owner: str, builder_cls: type, field_types: dict[str, str]) -> str:
    setter_names = []
    build_name = None
    for name, member in builder_cls.__dict__.items():
        if not inspect.isfunction(member) or name.startswith("__"):
            continue
        arity = sum(1 for p in inspect.signature(member).parameters if p != "self")
        if arity == 1:  # (self, value) -> fluent setter
            setter_names.append(name)
        elif arity == 0:  # (self) -> build
            build_name = name
    types_in_order = list(field_types.values())
    lines = ["class Builder:"]
    for index, setter in enumerate(setter_names):
        value_type = types_in_order[index] if index < len(types_in_order) else "Any"
        lines.append(f"    def {setter}(self, value: {value_type}) -> {owner}.Builder: ...")
    if build_name is not None:
        lines.append(f"    def {build_name}(self) -> {owner}: ...")
    if len(lines) == 1:
        lines.append("    ...")
    return "\n".join(lines)
