"""A lazy-resolving dependency-injection container: register once, build on first get()."""

from __future__ import annotations

import enum
import threading
from dataclasses import dataclass
from typing import Any, TypeVar, cast

from inito.di.dependency_resolver import (
    Dependency,
    registrable_type,
    resolve_constructor_dependencies,
)
from inito.exceptions.errors import (
    CircularDependencyError,
    DependencyRegistrationError,
    UnresolvableDependencyError,
)

T = TypeVar("T")


class Scope(enum.Enum):
    """How a registered service's lifetime is managed."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"


@dataclass(frozen=True)
class ServiceRegistration:
    """A registered service: its class, scope, and resolved constructor dependencies."""

    cls: type
    scope: Scope
    dependencies: dict[str, Dependency]


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
        self._locks_guard = threading.Lock()

    def register(self, cls: type, *, scope: Scope = Scope.SINGLETON) -> None:
        """Register cls's constructor dependency types under scope, without instantiating it."""
        if cls in self._registrations:
            raise DependencyRegistrationError(f"{cls!r} is already registered.")
        dependencies = resolve_constructor_dependencies(cls)
        self._registrations[cls] = ServiceRegistration(cls, scope, dependencies)

    def get(self, cls: type[T]) -> T:
        """Resolve and return an instance of cls, building its dependency graph bottom-up."""
        return cast(T, self._resolve(cls, path=()))

    def is_registered(self, cls: type) -> bool:
        """Whether cls has been registered in this container."""
        return cls in self._registrations

    def reset(self) -> None:
        """Clear the singleton instance cache (not registrations). Mainly for tests/reload."""
        self._singletons.clear()

    def _resolve(self, cls: type, path: tuple[type, ...]) -> Any:  # noqa: ANN401
        registration = self._registrations.get(cls)
        if registration is None:
            raise UnresolvableDependencyError(f"{cls!r} is not registered in the container.")
        if registration.scope is Scope.SINGLETON and cls in self._singletons:
            return self._singletons[cls]
        if cls in path:
            cycle = (*path, cls)
            raise CircularDependencyError(
                "Circular dependency detected: " + " -> ".join(step.__qualname__ for step in cycle)
            )
        if registration.scope is Scope.SINGLETON:
            return self._resolve_singleton(cls, registration, path)
        kwargs = self._resolve_dependencies(cls, registration, path)
        return cls(**kwargs)

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
        with self._lock_for(cls):
            if cls in self._singletons:
                return self._singletons[cls]
            instance = cls(**kwargs)
            self._singletons[cls] = instance
            return instance

    def _lock_for(self, cls: type) -> threading.Lock:
        with self._locks_guard:
            lock = self._singleton_locks.get(cls)
            if lock is None:
                lock = threading.Lock()
                self._singleton_locks[cls] = lock
            return lock

    def _resolve_dependencies(
        self, cls: type, registration: ServiceRegistration, path: tuple[type, ...]
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        for name, dependency in registration.dependencies.items():
            resolved_type = registrable_type(dependency.type_hint)
            if resolved_type in self._registrations:
                kwargs[name] = self._resolve(resolved_type, (*path, cls))
            elif not dependency.has_default:
                raise UnresolvableDependencyError(
                    f"{cls.__qualname__}.__init__ parameter {name!r} (type "
                    f"{dependency.type_hint!r}) isn't registered and has no default value."
                )
            # else: unregistered type with a default - omit, the constructor's own default applies
        return kwargs


default_container = Container()
"""Shared container that @Service/@Singleton register into by default."""
