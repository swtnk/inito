"""@Inject: auto-wires a function's type-annotated parameters from a DI container per call."""

from __future__ import annotations

import functools
import inspect
import typing
from typing import Any, Callable, Optional

from inito.di.container import Container, default_container
from inito.di.dependency_resolver import registrable_type

# (param_name, positional_index_or_None, resolved_type) computed once at decoration time.
_Injectable = tuple[str, Optional[int], Any]


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
    and documented rather than hidden. All signature/type-hint inspection is
    still done exactly once, at decoration time; the per-call path only checks
    which parameters the caller already supplied and resolves the rest.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        return _wrap(fn, container if container is not None else default_container)

    return decorator(func) if func is not None else decorator


def _collect_injectables(fn: Callable[..., Any]) -> list[_Injectable]:
    """Precompute, once, each annotated parameter's name, positional index, and resolved type.

    A parameter is injectable if it carries a type annotation. Its positional
    index (used per call to tell whether the caller already passed it
    positionally) is None for keyword-only parameters and for anything after a
    ``*args`` - those can only be supplied by keyword.
    """
    hints = typing.get_type_hints(fn, include_extras=True)
    hints.pop("return", None)
    injectables: list[_Injectable] = []
    positional_index = 0
    after_var_positional = False
    for param in inspect.signature(fn).parameters.values():
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            after_var_positional = True
            continue
        if param.kind is inspect.Parameter.VAR_KEYWORD:
            continue
        positional = param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        if param.name in hints:
            index = positional_index if (positional and not after_var_positional) else None
            injectables.append((param.name, index, registrable_type(hints[param.name])))
        if positional:
            positional_index += 1
    return injectables


def _wrap(fn: Callable[..., Any], target_container: Container) -> Callable[..., Any]:
    injectables = _collect_injectables(fn)

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401 -- forwards fn's own signature
        supplied_positional = len(args)
        for name, index, resolved_type in injectables:
            if name in kwargs or (index is not None and index < supplied_positional):
                continue
            if target_container.is_registered(resolved_type):
                kwargs[name] = target_container.get(resolved_type)
        return fn(*args, **kwargs)

    return wrapper


inject = Inject
