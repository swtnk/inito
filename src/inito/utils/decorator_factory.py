"""Shared factory for decorators that support both bare and parameterized use.

Every inito decorator (``@Data``, and later ``@Getter``, ``@Builder``, ...)
needs to support ``@Data``, ``@Data()``, and ``@Data(frozen=True)`` without
reimplementing that dispatch. ``make_decorator`` is the single place that
dance is implemented.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable, TypeVar

from inito.exceptions.errors import DecoratorConfigurationError

OptionsT = TypeVar("OptionsT")

_Apply = Callable[[type, OptionsT], type]


def make_decorator(apply: _Apply[OptionsT], default_options: OptionsT) -> Callable[..., Any]:
    """Build a decorator supporting both bare and call-with-options usage."""

    def decorator(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401 -- dual-mode dispatch
        if len(args) == 1 and not kwargs and isinstance(args[0], type):
            return apply(args[0], default_options)
        if len(args) > 1:
            raise DecoratorConfigurationError(
                "Decorators accept either a single class or configuration options, not both."
            )
        options = _resolve_options(args, kwargs, default_options)
        return lambda cls: apply(cls, options)

    return decorator


def _resolve_options(
    args: tuple[Any, ...], kwargs: dict[str, Any], default_options: OptionsT
) -> OptionsT:
    if args and kwargs:
        raise DecoratorConfigurationError(
            "Provide either a configuration options instance or keyword overrides, not both."
        )
    if args:
        (candidate,) = args
        if not isinstance(candidate, type(default_options)):
            raise DecoratorConfigurationError(
                f"Expected an instance of {type(default_options).__name__!r}, got {candidate!r}."
            )
        return candidate
    return dataclasses.replace(default_options, **kwargs)  # type: ignore[type-var]
