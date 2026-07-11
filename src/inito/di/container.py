"""A lazy-resolving dependency-injection container: register once, build on first get()."""

from __future__ import annotations

import contextlib
import enum
import threading
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, TypeVar, cast

from inito.di.dependency_resolver import (
    Dependency,
    resolve_constructor_dependencies,
)
from inito.exceptions.errors import (
    AmbiguousDependencyError,
    CircularDependencyError,
    DependencyRegistrationError,
    UnresolvableDependencyError,
)

T = TypeVar("T")

_MISSING = object()
"""Sentinel for 'no cached instance' - distinct from a legitimately falsy one."""


def _safe_issubclass(child: type, parent: Any) -> bool:  # noqa: ANN401 -- arbitrary base type
    """Return whether child subclasses parent, False if issubclass can't judge parent.

    A dependency's registrable type may be a parameterized generic (``list[int]``)
    or a non-runtime-checkable Protocol: ``issubclass(child, parent)`` raises
    TypeError for those (and, quirkily, ``isinstance(list[int], type)`` is True on
    some Python versions), so such a type is simply not an injectable interface.
    """
    try:
        return issubclass(child, parent)
    except TypeError:
        return False


class Scope(enum.Enum):
    """How a registered service's lifetime is managed."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    THREAD_LOCAL = "thread_local"


@dataclass(frozen=True)
class ServiceRegistration:
    """A registered service: its class, scope, resolved dependencies, and primary flag."""

    cls: type
    scope: Scope
    dependencies: dict[str, Dependency]
    primary: bool = False


class Container:
    """Registers services at decoration time; resolves and builds instances lazily on get().

    Singleton construction is thread-safe: concurrent first-access to the
    same singleton from multiple threads is serialized via a per-class
    lock, so a service is never constructed more than once and every
    caller receives the same instance. Already-cached singletons cost
    nothing extra - no lock is touched once resolved. A Container is
    always process-local; it is not shared across separate OS processes.
    """

    def __init__(self) -> None:
        """Create an empty container with no registrations."""
        self._registrations: dict[type, ServiceRegistration] = {}
        self._singletons: dict[type, Any] = {}
        self._singleton_locks: dict[type, threading.Lock] = {}
        self._overrides: dict[type, Callable[[], Any]] = {}
        self._thread_local = threading.local()
        self._qualified: dict[str, type] = {}

    def register(
        self,
        cls: type,
        *,
        scope: Scope = Scope.SINGLETON,
        qualifier: str | None = None,
        primary: bool = False,
    ) -> None:
        """Register cls under scope (and optional qualifier), without instantiating it."""
        if cls in self._registrations:
            raise DependencyRegistrationError(f"{cls!r} is already registered.")
        if qualifier is not None and qualifier in self._qualified:
            raise DependencyRegistrationError(
                f"Qualifier {qualifier!r} is already registered to {self._qualified[qualifier]!r}."
            )
        dependencies = resolve_constructor_dependencies(cls)
        self._registrations[cls] = ServiceRegistration(cls, scope, dependencies, primary)
        if qualifier is not None:
            self._qualified[qualifier] = cls
        if scope is Scope.SINGLETON:
            # Create the construction lock now, at (single-threaded) decoration
            # time, so the cold resolve path reads it with a plain dict lookup
            # instead of guarding a lazily-created-lock dict on every build.
            self._singleton_locks[cls] = threading.Lock()

    def get(self, cls: type[T]) -> T:
        """Resolve and return an instance of cls, building its dependency graph bottom-up."""
        # An active override wins over everything, including a cached singleton;
        # the empty-dict guard keeps this ~free when nothing is overridden (the
        # production case), so the warm fast-path is unregressed.
        if self._overrides:
            provider = self._overrides.get(cls)
            if provider is not None:
                return cast(T, provider())
        # Warm-singleton fast path: a single dict lookup, skipping registration
        # lookup / scope / cycle checks and even typing.cast (a real runtime call
        # here). A cached instance is never None, so a miss falls through to the
        # full resolve. This is the overwhelmingly common call once the graph is
        # built, so the returned-Any is silenced rather than paying for a cast.
        instance = self._singletons.get(cls)
        if instance is not None:
            return instance  # type: ignore[no-any-return]
        return cast(T, self._resolve(cls, path=()))

    def override(self, cls: type[T], instance: T) -> None:
        """Make get(cls) return instance until cleared. For tests/environment swaps."""
        self._overrides[cls] = lambda: instance

    def override_factory(self, cls: type[T], factory: Callable[[], T]) -> None:
        """Make get(cls) return factory() on each resolution until cleared."""
        self._overrides[cls] = factory

    def clear_override(self, cls: type) -> None:
        """Remove any override for cls."""
        self._overrides.pop(cls, None)

    def clear_overrides(self) -> None:
        """Remove all overrides."""
        self._overrides.clear()

    @contextlib.contextmanager
    def overrides(self, mapping: Mapping[type, Any]) -> Iterator[None]:
        """Temporarily override each type -> instance in mapping, restoring on exit.

        Both the overrides and the singleton cache are snapshotted and restored,
        so any singleton built *under* the override is discarded on exit and the
        container returns to its prior state - the behavior a test expects.
        """
        previous_overrides = dict(self._overrides)
        previous_singletons = dict(self._singletons)
        for cls, instance in mapping.items():
            self.override(cls, instance)
        try:
            yield
        finally:
            self._overrides = previous_overrides
            self._singletons = previous_singletons

    def is_registered(self, cls: type) -> bool:
        """Whether cls has been registered in this container."""
        return cls in self._registrations

    def reset(self) -> None:
        """Clear the singleton/thread-local caches and overrides (not registrations)."""
        self._singletons.clear()
        self._overrides.clear()
        self._thread_local = threading.local()

    def _thread_local_cache(self) -> dict[type, Any]:
        cache = getattr(self._thread_local, "cache", None)
        if cache is None:
            cache = {}
            self._thread_local.cache = cache
        return cache

    def _cached_instance(self, cls: type, scope: Scope) -> Any:  # noqa: ANN401
        if scope is Scope.SINGLETON:
            return self._singletons.get(cls, _MISSING)
        if scope is Scope.THREAD_LOCAL:
            return self._thread_local_cache().get(cls, _MISSING)
        return _MISSING

    def _resolve(self, cls: type, path: tuple[type, ...]) -> Any:  # noqa: ANN401
        if self._overrides:
            provider = self._overrides.get(cls)
            if provider is not None:
                return provider()
        registration = self._registrations.get(cls)
        if registration is None:
            raise UnresolvableDependencyError(f"{cls!r} is not registered in the container.")
        cached = self._cached_instance(cls, registration.scope)
        if cached is not _MISSING:
            return cached
        if cls in path:
            cycle = (*path, cls)
            raise CircularDependencyError(
                "Circular dependency detected: " + " -> ".join(step.__qualname__ for step in cycle)
            )
        return self._build(cls, registration, path)

    def _build(self, cls: type, registration: ServiceRegistration, path: tuple[type, ...]) -> Any:  # noqa: ANN401
        if registration.scope is Scope.SINGLETON:
            return self._resolve_singleton(cls, registration, path)
        instance = cls(**self._resolve_dependencies(cls, registration, path))
        if registration.scope is Scope.THREAD_LOCAL:
            self._thread_local_cache()[cls] = instance
        return instance

    def _resolve_singleton(
        self, cls: type, registration: ServiceRegistration, path: tuple[type, ...]
    ) -> Any:  # noqa: ANN401
        # Dependencies are resolved *before* taking cls's lock: each dependency is
        # itself resolved (and, if a singleton, cached) under its own lock, so no
        # thread ever holds two singleton locks at once. That keeps the critical
        # section to just construct-and-cache and, unlike holding cls's lock across
        # the whole recursive subtree, cannot deadlock two threads resolving a
        # cyclic graph from opposite ends. Double-checked locking keeps the
        # warm/cached path lock-free (checked in _resolve before we get here).
        kwargs = self._resolve_dependencies(cls, registration, path)
        # The lock was created for this singleton at register() time, so this is
        # a plain (thread-safe) dict read - no guard lock needed on the cold path.
        with self._singleton_locks[cls]:
            if cls in self._singletons:
                return self._singletons[cls]
            instance = cls(**kwargs)
            self._singletons[cls] = instance
            return instance

    def _resolve_dependencies(
        self, cls: type, registration: ServiceRegistration, path: tuple[type, ...]
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        for name, dependency in registration.dependencies.items():
            resolved = self._resolve_dependency(cls, name, dependency, path)
            if resolved is not _MISSING:
                kwargs[name] = resolved
        return kwargs

    def _resolve_dependency(
        self, cls: type, name: str, dependency: Dependency, path: tuple[type, ...]
    ) -> Any:  # noqa: ANN401
        child_path = (*path, cls)
        if dependency.qualifier is not None:
            target = self._qualified.get(dependency.qualifier)
            if target is None:
                raise UnresolvableDependencyError(
                    f"{cls.__qualname__}.__init__ parameter {name!r} requests qualifier "
                    f"{dependency.qualifier!r}, which is not registered."
                )
            return self._resolve(target, child_path)
        resolved_type = dependency.registrable  # precomputed at registration time
        if resolved_type in self._registrations:
            return self._resolve(resolved_type, child_path)
        implementation = self._pick_implementation(resolved_type)
        if implementation is not None:
            return self._resolve(implementation, child_path)
        if dependency.has_default:
            return _MISSING  # unregistered + default -> omit, the ctor's own default applies
        raise UnresolvableDependencyError(
            f"{cls.__qualname__}.__init__ parameter {name!r} (type "
            f"{dependency.type_hint!r}) isn't registered and has no default value."
        )

    def _pick_implementation(self, base_type: Any) -> type | None:  # noqa: ANN401
        """Return the sole or primary registered subclass of an unregistered base, if any."""
        if not isinstance(base_type, type):
            return None
        candidates = [
            registration.cls
            for registration in self._registrations.values()
            if registration.cls is not base_type and _safe_issubclass(registration.cls, base_type)
        ]
        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            return None
        primaries = [cls for cls in candidates if self._registrations[cls].primary]
        if len(primaries) == 1:
            return primaries[0]
        raise AmbiguousDependencyError(
            f"{base_type.__qualname__} has multiple registered implementations "
            f"({', '.join(cls.__qualname__ for cls in candidates)}); mark one "
            "@Service(primary=True) or inject Annotated[..., Qualifier(name)]."
        )


default_container = Container()
"""Shared container that @Service/@Singleton register into by default."""
