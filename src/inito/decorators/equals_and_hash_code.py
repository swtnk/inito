"""@EqualsAndHashCode: generates __eq__ and __hash__ over every declared field."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class EqualsAndHashCodeOptions:
    """Configuration surface for the @EqualsAndHashCode decorator (no options yet)."""


def _apply_equals_and_hash_code(cls: type, options: EqualsAndHashCodeOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "eq")
    attach_capability(cls, metadata, "hash")
    return cls


EqualsAndHashCode = make_decorator(_apply_equals_and_hash_code, EqualsAndHashCodeOptions())
EqualsAndHashCode.__doc__ = "Generate __eq__ and __hash__ over every declared field."
equals_and_hash_code = EqualsAndHashCode
