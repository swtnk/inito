"""@Service: registers a class's constructor dependencies into a DI container."""

from __future__ import annotations

from dataclasses import dataclass

from inito.di.container import Container, Scope, default_container
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class ServiceOptions:
    """Configuration surface for the @Service decorator."""

    scope: Scope = Scope.SINGLETON
    container: Container | None = None


def _apply_service(cls: type, options: ServiceOptions) -> type:
    target = options.container if options.container is not None else default_container
    target.register(cls, scope=options.scope)
    return cls


Service = make_decorator(_apply_service, ServiceOptions())
Service.__doc__ = (
    "Register cls's constructor dependency types into a Container (default_container "
    "unless container= is given), at decoration time - never instantiates cls. The class "
    "remains a perfectly ordinary, directly-constructible Python class; container.get(cls) "
    "is the DI-aware path that autowires and builds it."
)
Component = Service
service = Service
component = Component
