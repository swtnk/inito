"""@NoArgsConstructor: generates a no-argument __init__ using field defaults."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.reflection.introspection import reject_pydantic_target
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class NoArgsConstructorOptions:
    """Configuration surface for the @NoArgsConstructor decorator (no options yet)."""


def _apply_no_args_constructor(cls: type, options: NoArgsConstructorOptions) -> type:
    reject_pydantic_target(cls, "@NoArgsConstructor")
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "no_args_constructor")
    return cls


NoArgsConstructor = make_decorator(_apply_no_args_constructor, NoArgsConstructorOptions())
NoArgsConstructor.__doc__ = (
    "Generate a no-argument __init__ that assigns every field its default. "
    "Every field must have a default or default_factory, or decoration raises "
    "InvalidFieldDefinitionError."
)
no_args_constructor = NoArgsConstructor
