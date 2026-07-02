"""@Value: an immutable-style data class - constructor, repr, eq/hash, getters, no setters."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class ValueOptions:
    """Configuration surface for the @Value decorator."""

    include_getters: bool = True


def _apply_value(cls: type, options: ValueOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "constructor")
    attach_capability(cls, metadata, "repr")
    attach_capability(cls, metadata, "eq")
    attach_capability(cls, metadata, "hash")
    if options.include_getters:
        attach_capability(cls, metadata, "getter")
    return cls


Value = make_decorator(_apply_value, ValueOptions())
Value.__doc__ = (
    "Generate an immutable-style data class: constructor, __repr__, __eq__, "
    "__hash__, and ``get_`` accessors for every declared field - never "
    "setters. Stack with @dataclass(frozen=True) for genuine attribute-write "
    "immutability; on its own, @Value only omits setters, it doesn't block "
    "direct attribute assignment."
)
value = Value
