"""@Inject: auto-wires a function's type-annotated parameters from a DI container per call."""

from __future__ import annotations

import functools
import inspect
import typing
from typing import Any, Callable

from inito.di.container import Container, default_container
from inito.di.dependency_resolver import registrable_type


def Inject(  # noqa: N802 -- PascalCase matches every other inito decorator
    func: Callable[..., Any] | None = None,
    *,
    container: Container | None = None,
) -> Any:  # noqa: ANN401 -- dual-mode dispatch, returns either a wrapped function or a decorator
    """Wrap fn so its type-annotated, unfilled parameters are resolved from a Container per call.

    Explicit args/kwargs supplied by the caller are never overridden. Unlike
    every class decorator in this library, resolution here is a real per-call
    cost (a container.get() per unfilled, container-registered parameter) -
    @Inject targets composition-root entry points (e.g. a main()/handler
    function), not generated hot-path methods, so this cost is intentional
    and documented rather than hidden.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        return _wrap(fn, container if container is not None else default_container)

    return decorator(func) if func is not None else decorator


def _wrap(fn: Callable[..., Any], target_container: Container) -> Callable[..., Any]:
    hints = typing.get_type_hints(fn, include_extras=True)
    hints.pop("return", None)
    signature = inspect.signature(fn)
    injectable_params = tuple(name for name in signature.parameters if name in hints)

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401 -- forwards fn's own signature
        bound = signature.bind_partial(*args, **kwargs)
        for name in injectable_params:
            if name in bound.arguments:
                continue
            resolved_type = registrable_type(hints[name])
            if target_container.is_registered(resolved_type):
                kwargs[name] = target_container.get(resolved_type)
        return fn(*args, **kwargs)

    return wrapper


inject = Inject
