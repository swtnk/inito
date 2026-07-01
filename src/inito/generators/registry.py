"""Looks up generator instances by capability name.

New decorators are added by registering a new generator here, never by
modifying an existing generator's implementation.
"""

from __future__ import annotations

from typing import Union

from inito.exceptions.errors import DuplicateGeneratorError
from inito.generators.base import MethodGenerator, MultiMethodGenerator

Generator = Union[MethodGenerator, MultiMethodGenerator]


class GeneratorRegistry:
    """Looks up generator instances by capability name."""

    def __init__(self) -> None:
        """Create an empty registry with no generators registered."""
        self._generators: dict[str, Generator] = {}

    def register(self, capability: str, generator: Generator) -> None:
        """Register generator under capability, failing on name collisions."""
        if capability in self._generators:
            raise DuplicateGeneratorError(
                f"A generator is already registered for capability {capability!r}."
            )
        self._generators[capability] = generator

    def get(self, capability: str) -> Generator:
        """Return the generator registered under capability."""
        try:
            return self._generators[capability]
        except KeyError as error:
            raise KeyError(f"No generator registered for capability {capability!r}.") from error


default_registry = GeneratorRegistry()
"""Shared registry populated with inito's built-in generators."""
