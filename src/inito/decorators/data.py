"""@Data: constructor, repr, eq, hash, and accessor generation in one decorator."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class DataOptions:
    """Configuration surface for the @Data decorator.

    frozen=True skips setter generation and makes every field genuinely
    immutable: attribute assignment/deletion always raise
    dataclasses.FrozenInstanceError after construction, no
    @dataclass(frozen=True) stacking required.
    """

    frozen: bool = False
    include_getters: bool = True
    include_setters: bool = True


def _apply_data(cls: type, options: DataOptions) -> type:
    metadata = default_extractor.extract(cls)
    # Immutability is attached before the constructor so the constructor
    # generator sees the blocking __setattr__ and assigns fields via
    # object.__setattr__; a non-frozen class keeps the faster plain
    # self.x = x. See generators/constructor.py::needs_object_setattr.
    if options.frozen:
        attach_capability(cls, metadata, "immutable")
    attach_capability(cls, metadata, "constructor")
    attach_capability(cls, metadata, "repr")
    attach_capability(cls, metadata, "eq")
    attach_capability(cls, metadata, "hash")
    if options.include_getters:
        attach_capability(cls, metadata, "getter")
    if not options.frozen and options.include_setters:
        attach_capability(cls, metadata, "setter")
    return cls


Data = make_decorator(_apply_data, DataOptions())
Data.__doc__ = (
    "Generate a constructor, __repr__, __eq__, __hash__, and ``get_``/``set_`` "
    "accessors for every declared field. Accepts DataOptions "
    "(frozen, include_getters, include_setters)."
)
data = Data
