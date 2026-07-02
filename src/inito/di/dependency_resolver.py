"""Resolves a class's constructor parameter types, once, for @Service/@Singleton registration."""

from __future__ import annotations

import inspect
import types
import typing
from dataclasses import dataclass
from typing import Any

from inito.exceptions.errors import DependencyRegistrationError
from inito.reflection.introspection import _self_reference_injected

_UNION_TYPE = getattr(types, "UnionType", None)
"""types.UnionType (X | Y's runtime type) only exists on Python 3.10+."""


@dataclass(frozen=True)
class Dependency:
    """A single constructor parameter's resolved type and whether it has a default value."""

    type_hint: Any
    has_default: bool


def registrable_type(type_hint: Any) -> Any:  # noqa: ANN401 -- accepts/returns an arbitrary type hint
    """Unwrap Optional[X]/X | None to X, so an optional dependency can still autowire.

    typing.get_type_hints also has version-dependent "implicit Optional"
    behavior for None-defaulted parameters (Python <= 3.10 wraps a bare
    ``X = None`` annotation as ``Optional[X]`` automatically); unwrapping
    here makes resolution consistent regardless of that quirk, and lets
    genuinely-written ``Optional[X] = None`` dependencies resolve too.
    Broader unions (Union[X, Y]) are left as-is - there's no single
    unambiguous type to autowire.
    """
    origin = typing.get_origin(type_hint)
    if origin is typing.Union or (_UNION_TYPE is not None and origin is _UNION_TYPE):
        args = [arg for arg in typing.get_args(type_hint) if arg is not type(None)]
        if len(args) == 1:
            return args[0]
    return type_hint


def resolve_constructor_dependencies(cls: type) -> dict[str, Dependency]:
    """Return {param_name: Dependency} for every __init__ parameter of cls except self.

    Resolved once, at @Service/@Singleton registration (decoration) time - never
    per Container.get() call. Every parameter must be type-annotated; a class
    with no custom __init__ has no dependencies.
    """
    # Walked via __mro__/__dict__ rather than `cls.__init__` - mypy flags the latter as an
    # unsound instance-attribute access on a `type` value, even though it's a class here.
    init = next(
        (klass.__dict__["__init__"] for klass in cls.__mro__ if "__init__" in klass.__dict__),
        object.__init__,
    )
    if init is object.__init__:
        return {}
    try:
        with _self_reference_injected(cls):
            hints = typing.get_type_hints(init, include_extras=True)
    except NameError as error:
        raise DependencyRegistrationError(
            f"Could not resolve constructor type hints for {cls.__qualname__!r}: {error}"
        ) from error
    hints.pop("return", None)
    params = inspect.signature(init).parameters
    dependencies: dict[str, Dependency] = {}
    for name, param in params.items():
        if name == "self":
            continue
        if name not in hints:
            raise DependencyRegistrationError(
                f"{cls.__qualname__}.__init__ parameter {name!r} has no type annotation; "
                "@Service requires every constructor parameter to be annotated."
            )
        dependencies[name] = Dependency(hints[name], param.default is not inspect.Parameter.empty)
    return dependencies
