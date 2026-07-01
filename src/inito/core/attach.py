"""The single point that mutates a class after code generation.

Every decorator ends up calling ``attach_capability``, which is the only
place a generated method is written onto a class. This keeps the
"attach once, at decoration time" performance rule auditable at a glance.
"""

from __future__ import annotations

from inito.builders.builder_generator import BuilderGenerator, BuilderOptions
from inito.generators.base import GeneratedMethod, generate_method, generate_methods
from inito.generators.registry import default_registry
from inito.metadata.class_metadata import ClassMetadata


def attach_method(cls: type, generated: GeneratedMethod) -> None:
    """Attach a single generated method directly onto cls's namespace."""
    generated.callable.__module__ = cls.__module__
    setattr(cls, generated.name, generated.callable)


def attach_capability(cls: type, metadata: ClassMetadata, capability: str) -> None:
    """Resolve capability from the registry, generate, and attach it to cls."""
    generator = default_registry.get(capability)
    if hasattr(generator, "generate_all"):
        methods = generate_methods(generator, metadata)  # type: ignore[arg-type]
    else:
        methods = (generate_method(generator, metadata),)
    for method in methods:
        attach_method(cls, method)


def attach_builder(cls: type, metadata: ClassMetadata, options: BuilderOptions) -> None:
    """Attach a nested Builder class, builder(), and optional to_builder() to cls."""
    generator = BuilderGenerator()
    cls.Builder = generator.build_builder_class(metadata, options)  # type: ignore[attr-defined]
    cls.builder = classmethod(generator.build_factory(metadata))  # type: ignore[attr-defined]
    if options.to_builder:
        cls.to_builder = generator.build_to_builder(metadata)  # type: ignore[attr-defined]
