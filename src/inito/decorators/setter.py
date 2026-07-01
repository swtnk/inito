"""@Setter: generates set_<field>(value) mutator methods for every declared field."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class SetterOptions:
    """Configuration surface for the @Setter decorator (no options yet)."""


def _apply_setter(cls: type, options: SetterOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "setter")
    return cls


Setter = make_decorator(_apply_setter, SetterOptions())
Setter.__doc__ = "Generate a set_<field>(value) mutator method for every declared field."
setter = Setter
