"""@Singleton: sugar for @Service that always registers with Scope.SINGLETON."""

from __future__ import annotations

from typing import Any

from inito.decorators.service import Service
from inito.di.container import Scope
from inito.exceptions.errors import DecoratorConfigurationError


def Singleton(*args: Any, **kwargs: Any) -> Any:  # noqa: N802, ANN401 -- PascalCase decorator name
    """Register cls into a Container with Scope.SINGLETON, always.

    A standalone decorator, not a stacking requirement on top of @Service -
    @Service(scope=...) already covers every scope, including singleton.
    Rejects an explicit scope= kwarg rather than silently honoring it, since
    a caller passing scope=Scope.TRANSIENT to @Singleton is almost certainly
    a mistake, not an intentional override.
    """
    if len(args) == 1 and not kwargs and isinstance(args[0], type):
        return Service(args[0])
    if "scope" in kwargs:
        raise DecoratorConfigurationError(
            "@Singleton always registers with Scope.SINGLETON; use @Service(scope=...) "
            "directly to choose a different scope."
        )
    return Service(scope=Scope.SINGLETON, **kwargs)


singleton = Singleton
