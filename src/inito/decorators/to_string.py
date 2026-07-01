"""@ToString: generates a __repr__ listing every declared field."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class ToStringOptions:
    """Configuration surface for the @ToString decorator (no options yet)."""


def _apply_to_string(cls: type, options: ToStringOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "repr")
    return cls


ToString = make_decorator(_apply_to_string, ToStringOptions())
to_string = ToString
