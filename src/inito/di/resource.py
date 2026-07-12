"""Resource lifecycle specs: how a ``@Resource`` class or provider function is torn down.

All detection here runs **once**, at decoration/registration time — never per
``get()``. The container reads the resulting specs to enter and finalize
resources; it never re-inspects a class or function.
"""

from __future__ import annotations

import collections.abc
import enum
import inspect
import typing
from dataclasses import dataclass
from typing import Any, Callable

from inito.exceptions.errors import DependencyRegistrationError

RESOURCE_ATTRIBUTE = "__inito_resource__"
"""Class attribute holding a class-form resource's ResourceSpec (a data marker)."""

_SYNC_ITERATOR_ORIGINS = frozenset(
    {collections.abc.Iterator, collections.abc.Generator, collections.abc.Iterable}
)
_ASYNC_ITERATOR_ORIGINS = frozenset(
    {collections.abc.AsyncIterator, collections.abc.AsyncGenerator, collections.abc.AsyncIterable}
)


class ProviderKind(enum.Enum):
    """The shape of a ``@Resource`` provider function."""

    SYNC_GENERATOR = "sync_generator"
    ASYNC_GENERATOR = "async_generator"


@dataclass(frozen=True)
class ResourceSpec:
    """How a ``@Resource`` *class* is finalized, resolved once at decoration time.

    Either ``close_method`` names a teardown method (``is_async`` iff it is a
    coroutine function), or ``is_context_manager`` is set — the container enters
    the instance on build and exits it at teardown.
    """

    close_method: str | None
    is_context_manager: bool
    is_async: bool


@dataclass(frozen=True)
class ProviderSpec:
    """A ``@Resource`` *generator-provider function* keyed by the type it yields."""

    factory: Callable[..., Any]
    provided_type: Any  # the yielded type; the container registration key
    kind: ProviderKind


def class_resource_spec(cls: type, close_name: str) -> ResourceSpec:
    """Determine how a ``@Resource`` class is torn down, once, at decoration time."""
    method = getattr(cls, close_name, None)
    if callable(method):
        return ResourceSpec(
            close_method=close_name,
            is_context_manager=False,
            is_async=inspect.iscoroutinefunction(method),
        )
    if hasattr(cls, "__exit__"):
        return ResourceSpec(close_method=None, is_context_manager=True, is_async=False)
    if hasattr(cls, "__aexit__"):
        raise DependencyRegistrationError(
            f"{cls.__qualname__}: @Resource does not yet support async context managers; "
            "give it an async close()/aclose() method instead."
        )
    raise DependencyRegistrationError(
        f"{cls.__qualname__}: a @Resource class needs a {close_name}() method or the "
        "context-manager protocol (__enter__/__exit__)."
    )


def provider_spec(fn: Callable[..., Any]) -> ProviderSpec:
    """Determine a ``@Resource`` provider function's kind and yielded type, once."""
    if inspect.isgeneratorfunction(fn):
        kind = ProviderKind.SYNC_GENERATOR
    elif inspect.isasyncgenfunction(fn):
        kind = ProviderKind.ASYNC_GENERATOR
    else:
        raise DependencyRegistrationError(
            f"{fn.__qualname__}: a @Resource function must be a generator that yields the "
            "resource and then cleans up (`obj = ...; yield obj; obj.close()`)."
        )
    return ProviderSpec(factory=fn, provided_type=_provided_type(fn), kind=kind)


def _provided_type(fn: Callable[..., Any]) -> Any:  # noqa: ANN401 -- arbitrary yielded type
    try:
        hints = typing.get_type_hints(fn)
    except NameError as error:
        raise DependencyRegistrationError(
            f"Could not resolve the return annotation of {fn.__qualname__!r}: {error}"
        ) from error
    return_hint = hints.get("return")
    origin = typing.get_origin(return_hint)
    if origin in _SYNC_ITERATOR_ORIGINS or origin in _ASYNC_ITERATOR_ORIGINS:
        args = typing.get_args(return_hint)
        if args:
            return args[0]
    raise DependencyRegistrationError(
        f"{fn.__qualname__}: a @Resource generator must annotate its return type as "
        "Iterator[X]/Generator[X, ...] (or the Async variants) so inito knows what it provides."
    )
