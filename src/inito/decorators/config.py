"""@Config: populate a class's fields from environment variables, once, at construction."""

from __future__ import annotations

import os
import typing
from dataclasses import dataclass
from typing import Any, Callable

from inito.core.attach import attach_method
from inito.exceptions.errors import ConfigResolutionError
from inito.generators.base import GeneratedMethod
from inito.metadata.field import FieldMetadata
from inito.utils.codegen import build_function
from inito.utils.decorator_factory import make_decorator

_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off"})

_FieldPlan = tuple[str, str, Callable[[str], Any], bool, Any]


@dataclass(frozen=True)
class ConfigOptions:
    """Configuration surface for the @Config decorator."""

    prefix: str = ""


def _to_bool(raw: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ValueError(f"{raw!r} is not a boolean")


def _coercer_for(type_hint: Any) -> Callable[[str], Any]:  # noqa: ANN401 -- arbitrary field type
    unwrapped = type_hint
    if typing.get_origin(type_hint) is typing.Union:
        args = [arg for arg in typing.get_args(type_hint) if arg is not type(None)]
        if len(args) == 1:
            unwrapped = args[0]
    if unwrapped is bool:
        return _to_bool
    if unwrapped is int:
        return int
    if unwrapped is float:
        return float
    return str


def _field_plan(field: FieldMetadata, prefix: str) -> _FieldPlan:
    env_key = f"{prefix}{field.name.upper()}"
    return (field.name, env_key, _coercer_for(field.type_hint), field.has_default, field.default)


def _build_loader(owner: str, plan: tuple[_FieldPlan, ...]) -> Callable[[Any], None]:
    def _load(instance: Any) -> None:  # noqa: ANN401 -- the config instance being populated
        for name, env_key, coerce, has_default, default in plan:
            raw = os.environ.get(env_key)
            if raw is not None:
                try:
                    setattr(instance, name, coerce(raw))
                except ValueError as error:
                    raise ConfigResolutionError(
                        f"{owner}: env {env_key!r}={raw!r} is invalid for field {name!r}: {error}"
                    ) from error
            elif has_default:
                setattr(instance, name, default)
            else:
                raise ConfigResolutionError(
                    f"{owner}: required config field {name!r} is missing (set env {env_key!r})"
                )

    return _load


def _apply_config(cls: type, options: ConfigOptions) -> type:
    from inito.metadata.extractor import default_extractor

    metadata = default_extractor.extract(cls)
    plan = tuple(_field_plan(field, options.prefix) for field in metadata.fields)
    loader = _build_loader(metadata.qualified_name, plan)
    init = build_function(
        "__init__",
        "def __init__(self):\n    _load_config(self)\n",
        {"_load_config": loader},
        f"{metadata.qualified_name}.__init__",
    )
    attach_method(cls, GeneratedMethod(name="__init__", callable=init))
    return cls


Config = make_decorator(_apply_config, ConfigOptions())
Config.__doc__ = (
    "Generate a zero-argument __init__ that loads each declared field from an "
    "environment variable (UPPER_SNAKE of the field name, with an optional "
    "prefix), coerced to the field's annotated type, at construction time. "
    "Fields without an env value fall back to their default; a required field "
    "with neither raises ConfigResolutionError. Register a @Config class as a "
    "@Service to autowire it by type. Accepts ConfigOptions(prefix)."
)
config = Config

__all__ = ["Config", "ConfigOptions", "config"]
