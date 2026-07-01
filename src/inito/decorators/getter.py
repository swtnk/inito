"""@Getter: generates get_<field>() accessor methods for every declared field."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class GetterOptions:
    """Configuration surface for the @Getter decorator (no options yet)."""


def _apply_getter(cls: type, options: GetterOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "getter")
    return cls


Getter = make_decorator(_apply_getter, GetterOptions())
Getter.__doc__ = "Generate a get_<field>() accessor method for every declared field."
getter = Getter
