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
builder = Builder

__all__ = ["Builder", "BuilderOptions", "builder"]
