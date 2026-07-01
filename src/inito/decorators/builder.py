"""@Builder: generates a fluent builder, `builder()`, and optional `to_builder()`."""

from __future__ import annotations

from inito.builders.builder_generator import BuilderOptions
from inito.core.attach import attach_builder
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


def _apply_builder(cls: type, options: BuilderOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_builder(cls, metadata, options)
    return cls


Builder = make_decorator(_apply_builder, BuilderOptions())
Builder.__doc__ = (
    "Generate a nested fluent Builder class, a builder() classmethod, and "
    "(with to_builder=True) a to_builder() instance method. Accepts "
    "BuilderOptions (to_builder, setter_prefix, build_method_name)."
)
builder = Builder

__all__ = ["Builder", "BuilderOptions", "builder"]
