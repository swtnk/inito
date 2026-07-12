"""A lazy-resolving dependency-injection container: register once, build on first get()."""

from __future__ import annotations

import contextlib
import enum
import threading
from collections.abc import Awaitable, Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Literal, TypeVar, cast

from inito.di.dependency_resolver import (
    Dependency,
    resolve_constructor_dependencies,
    resolve_provider_dependencies,
)
from inito.di.factory import Factory
from inito.di.resource import (
    RESOURCE_ATTRIBUTE,
    ProviderKind,
    ProviderSpec,
    ResourceSpec,
)
from inito.exceptions.errors import (
    AmbiguousDependencyError,
    CircularDependencyError,
    DependencyRegistrationError,
    ResourceTeardownError,
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
    resource: ResourceSpec | None = None  # class-form @Resource lifecycle
    provider: ProviderSpec | None = None  # function-form @Resource generator provider


@dataclass(frozen=True)
class _Finalizer:
    """A single resource's teardown, recorded at build time and run LIFO at shutdown.

    Exactly one of ``close``/``aclose`` is set; ``key`` is the registration whose
    cached singleton is dropped once torn down so a later ``get()`` rebuilds it.
    """

    key: type
    label: str
    close: Callable[[], Any] | None = None
    aclose: Callable[[], Awaitable[Any]] | None = None

    @property
    def is_async(self) -> bool:
        """Whether this resource must be torn down with ``await``."""
        return self.aclose is not None


def _advance_sync_generator(label: str, generator: Iterator[Any]) -> None:
    """Resume a provider generator past its ``yield`` to run its cleanup."""
    try:
        next(generator)
    except StopIteration:
        return
    raise ResourceTeardownError(f"{label}: a @Resource generator must yield exactly once.")


async def _advance_async_generator(label: str, generator: Any) -> None:  # noqa: ANN401 -- async gen
    """Resume an async provider generator past its ``yield`` to run its cleanup."""
    try:
        await generator.__anext__()
    except StopAsyncIteration:
        return
    raise ResourceTeardownError(f"{label}: a @Resource generator must yield exactly once.")


def _raise_teardown_errors(errors: list[tuple[str, BaseException]]) -> None:
    if errors:
        detail = "; ".join(f"{label}: {error!r}" for label, error in errors)
        raise ResourceTeardownError(f"resource teardown failed for {detail}")


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
        self._factory_plans: dict[type, dict[str, Dependency]] = {}
        self._resource_finalizers: list[_Finalizer] = []
        self._resource_lock = threading.Lock()

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
        resource = cls.__dict__.get(RESOURCE_ATTRIBUTE)
        if resource is not None and scope is not Scope.SINGLETON:
            raise DependencyRegistrationError(
                f"{cls.__qualname__}: @Resource requires singleton scope so its lifetime "
                "(and teardown) is container-managed."
            )
        self._registrations[cls] = ServiceRegistration(
            cls, scope, dependencies, primary, resource=resource
        )
        if qualifier is not None:
            self._qualified[qualifier] = cls
        if scope is Scope.SINGLETON:
            # Create the construction lock now, at (single-threaded) decoration
            # time, so the cold resolve path reads it with a plain dict lookup
            # instead of guarding a lazily-created-lock dict on every build.
            self._singleton_locks[cls] = threading.Lock()

    def register_provider(self, spec: ProviderSpec, *, scope: Scope = Scope.SINGLETON) -> None:
        """Register a function-form @Resource provider, keyed by the type it yields."""
        provided = spec.provided_type
        if provided in self._registrations:
            raise DependencyRegistrationError(f"{provided!r} is already registered.")
        if scope is not Scope.SINGLETON:
            raise DependencyRegistrationError("@Resource providers must be singleton-scoped.")
        dependencies = resolve_provider_dependencies(spec.factory)
        self._registrations[provided] = ServiceRegistration(
            provided, scope, dependencies, provider=spec
        )
        self._singleton_locks[provided] = threading.Lock()

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

    async def aget(self, cls: type[T]) -> T:
        """Async twin of ``get`` for building an async @Resource generator provider.

        Everything else (classes, sync providers, cached singletons) resolves through
        the synchronous path; only an async-generator provider is awaited to its first
        yield. Its own dependencies are resolved synchronously, so nesting an async
        provider as a constructor dependency of a sync-built class is not yet supported.
        """
        if self._overrides:
            provider = self._overrides.get(cls)
            if provider is not None:
                return cast(T, provider())
        instance = self._singletons.get(cls)
        if instance is not None:
            return instance  # type: ignore[no-any-return]
        registration = self._registrations.get(cls)
        if (
            registration is not None
            and registration.provider is not None
            and registration.provider.kind is ProviderKind.ASYNC_GENERATOR
        ):
            return cast(T, await self._aresolve_async_provider(cls, registration))
        return self.get(cls)

    async def _aresolve_async_provider(self, cls: type, registration: ServiceRegistration) -> Any:  # noqa: ANN401
        provider = cast(ProviderSpec, registration.provider)
        kwargs = self._resolve_dependencies(cls, registration, ())
        with self._singleton_locks[cls]:
            cached = self._singletons.get(cls)
            if (
                cached is not None
            ):  # pragma: no cover -- double-checked lock; only wins under a race
                return cached
            generator = provider.factory(**kwargs)
            value = await generator.__anext__()
            self._singletons[cls] = value
            label = cls.__qualname__
            self._record_finalizer(
                _Finalizer(
                    key=cls, label=label, aclose=lambda: _advance_async_generator(label, generator)
                )
            )
            return value

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
        """Clear the singleton/thread-local caches, overrides, and pending finalizers.

        Registrations are kept. A test helper: it drops resource finalizers **without**
        running them, so tear resources down with ``shutdown_resources()`` first if their
        cleanup matters.
        """
        self._singletons.clear()
        self._overrides.clear()
        self._thread_local = threading.local()
        with self._resource_lock:
            self._resource_finalizers = []

    def shutdown_resources(self) -> None:
        """Tear down every built @Resource in reverse construction order (LIFO).

        Best-effort: each is closed even if an earlier one raised, and the failures
        are aggregated into a single ``ResourceTeardownError``. Raises immediately,
        tearing nothing down, if an **async** resource is pending — use
        ``ashutdown_resources()`` / ``async with container`` for those.
        """
        with self._resource_lock:
            pending = self._resource_finalizers
            if any(finalizer.is_async for finalizer in pending):
                raise ResourceTeardownError(
                    "async @Resource teardown requires `await container.ashutdown_resources()` "
                    "or `async with container`."
                )
            self._resource_finalizers = []
        errors: list[tuple[str, BaseException]] = []
        for finalizer in reversed(pending):
            self._run_finalizer_sync(finalizer, errors)
        _raise_teardown_errors(errors)

    async def ashutdown_resources(self) -> None:
        """Async twin of ``shutdown_resources``: awaits async teardowns, runs sync ones."""
        with self._resource_lock:
            pending = self._resource_finalizers
            self._resource_finalizers = []
        errors: list[tuple[str, BaseException]] = []
        for finalizer in reversed(pending):
            try:
                if finalizer.aclose is not None:
                    await finalizer.aclose()
                else:
                    cast(Callable[[], Any], finalizer.close)()
            except Exception as error:  # teardown is best-effort; aggregated and re-raised below
                errors.append((finalizer.label, error))
            self._singletons.pop(finalizer.key, None)
        _raise_teardown_errors(errors)

    def _run_finalizer_sync(
        self, finalizer: _Finalizer, errors: list[tuple[str, BaseException]]
    ) -> None:
        try:
            cast(Callable[[], Any], finalizer.close)()
        except Exception as error:  # teardown is best-effort; aggregated and re-raised by caller
            errors.append((finalizer.label, error))
        self._singletons.pop(finalizer.key, None)

    def __enter__(self) -> Container:
        """Enter a ``with`` block; resources are still built lazily on first ``get()``."""
        return self

    def __exit__(self, *exc_info: object) -> Literal[False]:
        """Tear down all built resources on block exit."""
        self.shutdown_resources()
        return False

    async def __aenter__(self) -> Container:
        """Enter an ``async with`` block; resources are still built lazily."""
        return self

    async def __aexit__(self, *exc_info: object) -> Literal[False]:
        """Await teardown of all built resources on block exit."""
        await self.ashutdown_resources()
        return False

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
            instance, finalizer = self._construct(cls, registration, kwargs)
            self._singletons[cls] = instance
            if finalizer is not None:
                self._record_finalizer(finalizer)
            return instance

    def _construct(
        self, cls: type, registration: ServiceRegistration, kwargs: dict[str, Any]
    ) -> tuple[Any, _Finalizer | None]:
        """Build one instance, returning it with its teardown finalizer (or None)."""
        if registration.provider is not None:
            return self._construct_from_provider(cls, registration.provider, kwargs)
        instance = cls(**kwargs)
        if registration.resource is None:
            return instance, None
        return instance, self._class_finalizer(cls, instance, registration.resource)

    def _construct_from_provider(
        self, cls: type, provider: ProviderSpec, kwargs: dict[str, Any]
    ) -> tuple[Any, _Finalizer]:
        if provider.kind is ProviderKind.ASYNC_GENERATOR:
            raise UnresolvableDependencyError(
                f"{cls.__qualname__} is an async @Resource generator; build it with "
                "`await container.aget(...)` or inside `async with container`."
            )
        generator = provider.factory(**kwargs)
        value = next(generator)
        label = cls.__qualname__
        return value, _Finalizer(
            key=cls, label=label, close=lambda: _advance_sync_generator(label, generator)
        )

    def _class_finalizer(self, cls: type, instance: Any, resource: ResourceSpec) -> _Finalizer:  # noqa: ANN401
        label = cls.__qualname__
        if resource.is_context_manager:
            instance.__enter__()
            return _Finalizer(
                key=cls, label=label, close=lambda: instance.__exit__(None, None, None)
            )
        teardown = getattr(instance, cast(str, resource.close_method))
        if resource.is_async:
            return _Finalizer(key=cls, label=label, aclose=teardown)
        return _Finalizer(key=cls, label=label, close=teardown)

    def _record_finalizer(self, finalizer: _Finalizer) -> None:
        with self._resource_lock:
            self._resource_finalizers.append(finalizer)

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
        value = self._autowire(dependency, (*path, cls))
        if value is not _MISSING:
            return value
        if dependency.qualifier is not None:
            raise UnresolvableDependencyError(
                f"{cls.__qualname__}.__init__ parameter {name!r} requests qualifier "
                f"{dependency.qualifier!r}, which is not registered."
            )
        if dependency.has_default:
            return _MISSING  # unregistered + default -> omit, the ctor's own default applies
        raise UnresolvableDependencyError(
            f"{cls.__qualname__}.__init__ parameter {name!r} (type "
            f"{dependency.type_hint!r}) isn't registered and has no default value."
        )

    def _autowire(self, dependency: Dependency, path: tuple[type, ...]) -> Any:  # noqa: ANN401
        """Resolve dependency to an instance if its type is autowirable, else _MISSING.

        Shared by _resolve_dependency (which then raises or applies a default) and
        a Factory (which then applies call-time args or the target's own default).
        """
        if dependency.factory_target is not None:
            return self._make_factory(dependency.factory_target)
        if dependency.qualifier is not None:
            target = self._qualified.get(dependency.qualifier)
            return self._resolve(target, path) if target is not None else _MISSING
        resolved_type = dependency.registrable  # precomputed at registration time
        if resolved_type in self._registrations:
            return self._resolve(resolved_type, path)
        implementation = self._pick_implementation(resolved_type)
        if implementation is not None:
            return self._resolve(implementation, path)
        return _MISSING

    def _factory_plan(self, target: type) -> dict[str, Dependency]:
        plan = self._factory_plans.get(target)
        if plan is None:
            plan = resolve_constructor_dependencies(target)  # inspected once per target
            self._factory_plans[target] = plan
        return plan

    def _make_factory(self, target: type) -> Factory[Any]:
        return _BoundFactory(self, target, self._factory_plan(target))

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


class _BoundFactory(Factory[Any]):
    """A ``Factory[T]`` bound to a container: builds a fresh target per call.

    Call-time keyword arguments win; every other constructor parameter whose type
    is autowirable is resolved from the container; anything left falls to the
    target's own default (or a natural missing-argument ``TypeError`` at the call).
    The plan is the target's constructor dependencies, inspected once and cached.
    """

    def __init__(self, container: Container, target: type, plan: dict[str, Dependency]) -> None:
        self._container = container
        self._target = target
        self._plan = plan

    def __call__(self, **kwargs: Any) -> Any:  # noqa: ANN401 -- forwards to the target ctor
        final = dict(kwargs)  # call-time kwargs win over autowiring
        for name, dependency in self._plan.items():
            if name in final:
                continue
            value = self._container._autowire(dependency, ())
            if value is not _MISSING:
                final[name] = value
        return self._target(**final)


default_container = Container()
"""Shared container that @Service/@Singleton register into by default."""
