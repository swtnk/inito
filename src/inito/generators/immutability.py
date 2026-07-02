"""Generates __setattr__/__delattr__ that block all post-construction mutation.

Kept together deliberately, like EqGenerator/HashGenerator: a real frozen
class blocks both attribute write and delete. Every inito constructor
(``ConstructorGenerator``, ``NoArgsConstructorGenerator``,
``RequiredArgsConstructorGenerator``, ``BuilderGenerator``) already assigns
fields via ``object.__setattr__`` rather than plain assignment, specifically
so it bypasses whatever ``__setattr__`` ends up on the class - so attaching
this capability needs no change to any of them, and adds no construction-time
or attribute-read overhead (Python only consults ``__setattr__`` on writes).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any

from inito.generators.base import GeneratedMethod
from inito.metadata.class_metadata import ClassMetadata
from inito.utils.codegen import build_function

_GLOBALS: dict[str, Any] = {"FrozenInstanceError": FrozenInstanceError}

_SETATTR_SOURCE = (
    "def __setattr__(self, name, value):\n"
    '    raise FrozenInstanceError(f"cannot assign to field {name!r}")\n'
)

_DELATTR_SOURCE = (
    'def __delattr__(self, name):\n    raise FrozenInstanceError(f"cannot delete field {name!r}")\n'
)


class ImmutableGenerator:
    """Generates a __setattr__/__delattr__ pair blocking all post-construction mutation."""

    def generate_all(self, metadata: ClassMetadata) -> tuple[GeneratedMethod, ...]:
        """Return __setattr__ and __delattr__, both unconditionally raising FrozenInstanceError."""
        qualname = metadata.qualified_name
        setattr_fn = build_function(
            "__setattr__", _SETATTR_SOURCE, _GLOBALS, f"{qualname}.__setattr__"
        )
        delattr_fn = build_function(
            "__delattr__", _DELATTR_SOURCE, _GLOBALS, f"{qualname}.__delattr__"
        )
        return (
            GeneratedMethod(name="__setattr__", callable=setattr_fn),
            GeneratedMethod(name="__delattr__", callable=delattr_fn),
        )
