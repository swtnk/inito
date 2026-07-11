"""@AllArgsConstructor: generates a constructor accepting every declared field."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.reflection.introspection import reject_pydantic_target
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class AllArgsConstructorOptions:
    """Configuration surface for the @AllArgsConstructor decorator (no options yet)."""


def _apply_all_args_constructor(cls: type, options: AllArgsConstructorOptions) -> type:
    reject_pydantic_target(cls, "@AllArgsConstructor")
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "constructor")
    return cls


AllArgsConstructor = make_decorator(_apply_all_args_constructor, AllArgsConstructorOptions())
AllArgsConstructor.__doc__ = "Generate a constructor accepting every declared field."
all_args_constructor = AllArgsConstructor
