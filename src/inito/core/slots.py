"""Rebuilds a class with ``__slots__``.

Python fixes ``__slots__`` at class-creation time, so a post-hoc decorator
cannot retrofit them - the class must be recreated. Mirroring how ``attrs``
handles ``slots=True``: build a new class with the same name, bases, and
namespace plus ``__slots__``, drop the field defaults that would otherwise
collide with a slot (their values already live in the generated ``__init__``),
add a ``__weakref__`` slot when no base provides one, and repoint any
``__class__`` closure cell (a zero-argument ``super()`` in a user method) at the
new class. Capabilities are attached *after* rebuilding, so every generated
member already refers to the new class.
"""

from __future__ import annotations

import types

from inito.metadata.class_metadata import METADATA_ATTRIBUTE, ClassMetadata

_SKIP_KEYS = frozenset({"__dict__", "__weakref__"})


def rebuild_with_slots(cls: type, metadata: ClassMetadata) -> tuple[type, ClassMetadata]:
    """Recreate cls with ``__slots__`` and return it with metadata bound to it.

    Called after metadata extraction (so field defaults are already captured)
    and before any capability is attached, so every generated member is built
    against the new class.
    """
    new_cls = build_slotted_class(cls, metadata.field_names())
    new_metadata = ClassMetadata(
        owner=new_cls, fields=metadata.fields, qualified_name=new_cls.__qualname__
    )
    setattr(new_cls, METADATA_ATTRIBUTE, new_metadata)
    return new_cls, new_metadata


def build_slotted_class(cls: type, slot_names: tuple[str, ...]) -> type:
    """Return a new class identical to cls but carrying ``__slots__``."""
    namespace = {
        key: value
        for key, value in cls.__dict__.items()
        if key not in _SKIP_KEYS and key not in slot_names
    }
    slots = slot_names if _inherits_weakref(cls) else (*slot_names, "__weakref__")
    namespace["__slots__"] = slots
    new_cls = type(cls)(cls.__name__, cls.__bases__, namespace)
    new_cls.__qualname__ = cls.__qualname__
    _repoint_class_cells(new_cls, cls)
    return new_cls


def _inherits_weakref(cls: type) -> bool:
    return any("__weakref__" in vars(base) for base in cls.__mro__[1:])


def _repoint_class_cells(new_cls: type, old_cls: type) -> None:
    for value in new_cls.__dict__.values():
        func = getattr(value, "__func__", value)
        if not isinstance(func, types.FunctionType):
            continue
        for cell in func.__closure__ or ():
            try:
                if cell.cell_contents is old_cls:
                    cell.cell_contents = new_cls
            except ValueError:  # pragma: no cover -- empty cell, nothing to repoint
                pass
