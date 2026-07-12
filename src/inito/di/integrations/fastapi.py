"""``Injected[T]``: resolve a service from an inito Container in a FastAPI handler.

FastAPI is an **optional** dependency, imported lazily inside the helpers here —
inito's runtime never imports it. Absent, using ``Injected`` raises a clear
``FrameworkIntegrationError``.
"""

from __future__ import annotations

from typing import Annotated, Any, Callable, cast

from inito.di.container import Container, default_container
from inito.exceptions.errors import FrameworkIntegrationError


def _load_depends() -> Callable[..., Any]:
    try:
        from fastapi import Depends
    except ModuleNotFoundError as error:  # pragma: no cover -- exercised via a stubbed import path
        raise FrameworkIntegrationError(
            "inito.Injected requires FastAPI; install it with `pip install fastapi`."
        ) from error
    return cast("Callable[..., Any]", Depends)


def _resolver(cls: Any, container: Container) -> Callable[[], Any]:  # noqa: ANN401 -- resolved type
    async def _provide() -> Any:  # noqa: ANN401 -- yields an instance of cls
        async with container.scope():
            yield await container.aget(cls)

    return _provide


def _depends(cls: Any, container: Container | None) -> Any:  # noqa: ANN401 -- FastAPI Depends marker
    depends = _load_depends()
    return depends(_resolver(cls, container if container is not None else default_container))


class Injected:
    """A FastAPI dependency that resolves ``T`` from an inito Container per request.

    Two equivalent forms::

        def handler(svc: Injected[Service]) -> ...:            # Annotated form
        def handler(svc: Service = Injected(Service)) -> ...:  # default-value form

    Each resolution runs inside a fresh ``container.scope()`` (opened and torn down
    per request), so a scoped ``@Resource`` — e.g. a request-lifetime DB session —
    is built on entry and closed when the request ends. Pass ``container=`` to the
    call form to resolve from a container other than the default.
    """

    def __class_getitem__(cls, item: Any) -> Any:  # noqa: ANN401 -- Annotated[item, Depends]
        """Return ``Annotated[item, Depends(resolver)]`` for use as a parameter annotation."""
        return Annotated[item, _depends(item, None)]

    def __new__(cls, target: type[Any], *, container: Container | None = None) -> Any:  # noqa: ANN401
        """Return a FastAPI ``Depends`` marker for use as a parameter default value.

        Typed ``Any`` so ``param: Service = Injected(Service)`` type-checks; the
        parameter's own ``Service`` annotation carries the real type.
        """
        return _depends(target, container)
