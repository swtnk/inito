"""@Value: a genuinely immutable data class - constructor, repr, eq/hash, getters, no setters."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.core.slots import rebuild_with_slots
from inito.metadata.extractor import default_extractor
from inito.reflection.introspection import reject_pydantic_target
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class ValueOptions:
    """Configuration surface for the @Value decorator.

    freeze_collections=True stores a mutable collection field as an immutable
    one (list->tuple, set->frozenset, dict->read-only mapping) at construction,
    hardening the shallow freeze that @Value already provides.
    """

    include_getters: bool = True
    slots: bool = False
    freeze_collections: bool = False


def _apply_value(cls: type, options: ValueOptions) -> type:
    reject_pydantic_target(cls, "@Value")
    metadata = default_extractor.extract(cls)
    if options.slots:
        cls, metadata = rebuild_with_slots(cls, metadata)
    # Immutability is attached before the constructor so the constructor
    # assigns via object.__setattr__ (bypassing the blocking __setattr__)
    # rather than a plain self.x = x. See generators/constructor.py.
    attach_capability(cls, metadata, "immutable")
    constructor = "freezing_constructor" if options.freeze_collections else "constructor"
    attach_capability(cls, metadata, constructor)
    attach_capability(cls, metadata, "repr")
    attach_capability(cls, metadata, "eq")
    attach_capability(cls, metadata, "hash")
    if options.include_getters:
        attach_capability(cls, metadata, "getter")
    return cls


Value = make_decorator(_apply_value, ValueOptions())
Value.__doc__ = (
    "Generate a genuinely immutable data class: constructor, __repr__, "
    "__eq__, __hash__, and ``get_`` accessors for every declared field - "
    "never setters. Attribute assignment and deletion always raise "
    "dataclasses.FrozenInstanceError after construction, unconditionally - "
    "no @dataclass(frozen=True) stacking required."
)
value = Value
