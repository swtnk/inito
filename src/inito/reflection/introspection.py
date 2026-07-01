"""Low-level annotation and MRO inspection helpers used at decoration time."""

from __future__ import annotations

import typing
from typing import Any

from inito.exceptions.errors import AnnotationResolutionError


def collect_ordered_field_names(cls: type) -> tuple[str, ...]:
    """Return every annotated field name across cls's MRO, in declaration order."""
    ordered: dict[str, None] = {}
    for klass in reversed(cls.__mro__[:-1]):
        for name in klass.__dict__.get("__annotations__", {}):
            ordered.setdefault(name, None)
    return tuple(ordered)


def resolve_type_hints(cls: type) -> dict[str, Any]:
    """Resolve cls's annotations to real type objects, once."""
    try:
        return typing.get_type_hints(cls, include_extras=True)
    except NameError as error:
        raise AnnotationResolutionError(
            f"Could not resolve type hints for {cls.__qualname__!r}: {error}"
        ) from error


def is_class_var(type_hint: Any) -> bool:  # noqa: ANN401 -- inspects an arbitrary resolved hint
    """Whether type_hint is a typing.ClassVar annotation."""
    return typing.get_origin(type_hint) is typing.ClassVar
