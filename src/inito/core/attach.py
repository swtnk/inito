"""The single point that mutates a class after code generation.

Every decorator ends up calling ``attach_capability``, which is the only
place a generated method is written onto a class. This keeps the
"attach once, at decoration time" performance rule auditable at a glance.
"""

from __future__ import annotations

import dataclasses

from inito.builders.builder_generator import BuilderGenerator, BuilderOptions
from inito.generators.base import GeneratedMethod, generate_method, generate_methods
from inito.generators.registry import default_registry
from inito.metadata.class_metadata import ClassMetadata

GENERATED_MARKER = "_inito_generated"
"""Attribute stamped on every generated member so `inito-stubgen` can find them."""

_DATACLASS_MANAGED = frozenset(
    {"__init__", "__repr__", "__eq__", "__hash__", "__setattr__", "__delattr__"}
)
"""Dunders a stacked ``@dataclass`` synthesizes; inito is meant to take these
over when it decorates a dataclass, so they are never treated as user code."""


def attach_method(cls: type, generated: GeneratedMethod) -> None:
    """Attach a generated method onto cls, unless the user already defined it.

    A member the user wrote in the class body (its own ``__repr__``, ``__eq__``,
    ...) is left untouched - inito never silently clobbers hand-written code.
    inito's own earlier-generated members carry the ``_inito_generated`` marker,
    so a stacked/re-applied decorator can still overwrite those.
    """
    if _user_defined(cls, generated.name):
        return
    generated.callable.__module__ = cls.__module__
    generated.callable._inito_generated = True  # type: ignore[attr-defined]
    setattr(cls, generated.name, generated.callable)


def attach_unhashable(cls: type) -> None:
    """Mark cls unhashable, as ``dataclasses`` does for a mutable value class.

    Sets ``__hash__ = None`` unless the user defined their own ``__hash__``.
    """
    if _user_defined(cls, "__hash__"):
        return
    cls.__hash__ = None  # type: ignore[assignment]


def _user_defined(cls: type, name: str) -> bool:
    existing = cls.__dict__.get(name)
    if existing is None or getattr(existing, "_inito_generated", False):
        return False
    return not (dataclasses.is_dataclass(cls) and name in _DATACLASS_MANAGED)


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
    builder_class = generator.build_builder_class(metadata, options)
    builder_class._inito_generated = True  # type: ignore[attr-defined]
    cls.Builder = builder_class  # type: ignore[attr-defined]
    factory = generator.build_factory(metadata)
    factory._inito_generated = True  # type: ignore[attr-defined]
    cls.builder = classmethod(factory)  # type: ignore[attr-defined]
    if options.to_builder:
        to_builder = generator.build_to_builder(metadata)
        to_builder._inito_generated = True  # type: ignore[attr-defined]
        cls.to_builder = to_builder  # type: ignore[attr-defined]
