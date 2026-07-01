"""Protocols and drivers turning field metadata into generated methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from inito.metadata.class_metadata import ClassMetadata
from inito.utils.codegen import build_function


@dataclass(frozen=True)
class GeneratedMethod:
    """A single generated method, ready to attach to a class."""

    name: str
    callable: Callable[..., Any]


class MethodGenerator(Protocol):
    """Produces one generated method's source and globals from metadata."""

    method_name: str

    def generate_source(self, metadata: ClassMetadata) -> str:
        """Return the complete ``def <method_name>(...): ...`` source block."""

    def build_globals(self, metadata: ClassMetadata) -> dict[str, Any]:
        """Return the globals namespace the generated source executes against."""


class MultiMethodGenerator(Protocol):
    """Produces several generated methods (e.g. one per field) from metadata."""

    def generate_all(self, metadata: ClassMetadata) -> tuple[GeneratedMethod, ...]:
        """Return every method this generator produces for metadata."""


def generate_method(generator: MethodGenerator, metadata: ClassMetadata) -> GeneratedMethod:
    """Compile a single-method generator's source into a GeneratedMethod."""
    source = generator.generate_source(metadata)
    globals_ns = generator.build_globals(metadata)
    qualname = f"{metadata.qualified_name}.{generator.method_name}"
    function = build_function(generator.method_name, source, globals_ns, qualname)
    return GeneratedMethod(name=generator.method_name, callable=function)


def generate_methods(
    generator: MultiMethodGenerator, metadata: ClassMetadata
) -> tuple[GeneratedMethod, ...]:
    """Compile a multi-method generator's output for metadata."""
    return generator.generate_all(metadata)
