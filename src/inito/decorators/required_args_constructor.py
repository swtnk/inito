"""@RequiredArgsConstructor: generates a constructor accepting only required fields."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.reflection.introspection import reject_pydantic_target
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class RequiredArgsConstructorOptions:
    """Configuration surface for the @RequiredArgsConstructor decorator (no options yet)."""


def _apply_required_args_constructor(cls: type, options: RequiredArgsConstructorOptions) -> type:
    reject_pydantic_target(cls, "@RequiredArgsConstructor")
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "required_args_constructor")
    return cls


RequiredArgsConstructor = make_decorator(
    _apply_required_args_constructor, RequiredArgsConstructorOptions()
)
RequiredArgsConstructor.__doc__ = (
    "Generate a constructor accepting only fields without a default; "
    "defaulted fields still get their default value assigned."
)
required_args_constructor = RequiredArgsConstructor
