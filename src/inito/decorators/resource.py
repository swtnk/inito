"""@Resource: mark a class or generator function whose instance the container must close."""

from __future__ import annotations

import dataclasses
import inspect
from dataclasses import dataclass
from typing import Any

from inito.di.container import Container, Scope, default_container
from inito.di.resource import RESOURCE_ATTRIBUTE, class_resource_spec, provider_spec
from inito.exceptions.errors import DecoratorConfigurationError


@dataclass(frozen=True)
class ResourceOptions:
    """Configuration surface for the @Resource decorator."""

    close: str = "close"
    container: Container | None = None
    scope: Scope = Scope.SINGLETON


def _apply_resource(target: Any, options: ResourceOptions) -> Any:  # noqa: ANN401 -- class or function
    if isinstance(target, type):
        spec = class_resource_spec(target, options.close)
        setattr(target, RESOURCE_ATTRIBUTE, spec)
        return target
    container = options.container if options.container is not None else default_container
    container.register_provider(provider_spec(target), scope=options.scope)
    return target


def _is_target(candidate: Any) -> bool:  # noqa: ANN401 -- decorator argument
    return isinstance(candidate, type) or inspect.isfunction(candidate)


def Resource(*args: Any, **kwargs: Any) -> Any:  # noqa: N802, ANN401 -- PascalCase dual-mode decorator
    """Mark a resource whose lifetime the container manages, then closes at shutdown.

    On a **class** (paired with @Service/@Singleton): the instance is torn down by
    its ``close()`` method — rename it with ``@Resource(close="aclose")`` — or, if
    it has none, the ``__enter__``/``__exit__`` protocol. An ``async`` close is
    awaited by ``ashutdown_resources()`` / ``async with container``.

    On a **generator function**: it self-registers a provider keyed by the yielded
    type; its parameters are autowired; the code after ``yield`` runs at teardown.
    Sync generators build via ``get()``, async generators via ``await aget()``.
    """
    if len(args) == 1 and not kwargs and _is_target(args[0]):
        return _apply_resource(args[0], ResourceOptions())
    if len(args) > 1:
        raise DecoratorConfigurationError(
            "@Resource accepts either a single class/function or configuration options."
        )
    options = _resolve_options(args, kwargs)
    return lambda target: _apply_resource(target, options)


def _resolve_options(args: tuple[Any, ...], kwargs: dict[str, Any]) -> ResourceOptions:
    if args and kwargs:
        raise DecoratorConfigurationError(
            "Provide either a ResourceOptions instance or keyword overrides, not both."
        )
    if args:
        (candidate,) = args
        if not isinstance(candidate, ResourceOptions):
            raise DecoratorConfigurationError(
                f"Expected a ResourceOptions instance, got {candidate!r}."
            )
        return candidate
    return dataclasses.replace(ResourceOptions(), **kwargs)


resource = Resource

__all__ = ["Resource", "ResourceOptions", "resource"]
