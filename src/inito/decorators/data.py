"""@Data: constructor, repr, eq, hash, and accessor generation in one decorator."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class DataOptions:
    """Configuration surface for the @Data decorator.

    Note: frozen=True only skips setter generation in this release; it does
    not yet enforce attribute-write immutability (tracked in TASKS.md).
    """

    frozen: bool = False
    include_getters: bool = True
    include_setters: bool = True


def _apply_data(cls: type, options: DataOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "constructor")
    attach_capability(cls, metadata, "repr")
    attach_capability(cls, metadata, "eq")
    attach_capability(cls, metadata, "hash")
    if options.include_getters:
        attach_capability(cls, metadata, "getter")
    if options.include_setters and not options.frozen:
        attach_capability(cls, metadata, "setter")
    return cls


Data = make_decorator(_apply_data, DataOptions())
Data.__doc__ = (
    "Generate a constructor, __repr__, __eq__, __hash__, and ``get_``/``set_`` "
    "accessors for every declared field. Accepts DataOptions "
    "(frozen, include_getters, include_setters)."
)
data = Data
