"""``Factory[T]``: inject a factory that builds ``T`` on demand with call-time args."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Factory(Generic[T]):
    """A callable that builds a fresh ``T`` per call, autowiring what it can.

    Inject it as a constructor parameter — ``make: Factory[Widget]`` — and call it
    to build a ``Widget`` on demand::

        report = self.make_report(title="Sales")   # title supplied now, deps autowired

    Every keyword argument you pass wins; every other constructor parameter of the
    target whose type is a registered service is autowired from the container; and
    anything left falls to the target's own default (or raises a natural
    missing-argument error). A fresh instance is built on every call — the result
    is never cached, and the target need not itself be registered.

    ``Factory`` is the annotation/marker and the static type: type-checkers see
    ``make(...)`` returning ``T`` with no plugin. The container injects a bound
    implementation; calling ``Factory`` directly is not supported.
    """

    def __call__(self, **kwargs: Any) -> T:  # noqa: ANN401 -- call-time args forwarded to T
        """Build and return a fresh ``T``; the injected implementation does the work."""
        raise NotImplementedError("Factory is injected by a Container; do not construct it.")
