"""@Resource lifecycle: class close()/context-manager + generator providers, sync & async."""

import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest

from inito.decorators.resource import Resource, ResourceOptions
from inito.decorators.service import Service
from inito.di.container import Container, Scope
from inito.di.resource import class_resource_spec, provider_spec
from inito.exceptions.errors import (
    DecoratorConfigurationError,
    DependencyRegistrationError,
    ResourceTeardownError,
    UnresolvableDependencyError,
)


class Ledger:
    """Records the order in which resources open and close, for ordering assertions."""

    events: list[str] = []  # noqa: RUF012 -- reset per test by the autouse fixture

    @classmethod
    def record(cls, event: str) -> None:
        cls.events.append(event)


@pytest.fixture(autouse=True)
def _reset_ledger() -> None:
    Ledger.events = []


# --- class form: close() method -------------------------------------------------


def test_class_close_is_called_on_shutdown():
    container = Container()

    @Service(container=container)
    @Resource
    class Db:
        def close(self) -> None:
            Ledger.record("close")

    container.get(Db)
    container.shutdown_resources()

    assert Ledger.events == ["close"]


def test_resources_torn_down_in_reverse_order():
    container = Container()

    def resource_named(name: str) -> type:
        @Service(container=container)
        @Resource
        class Res:
            def close(self) -> None:
                Ledger.record(name)

        return Res

    for name in ("first", "second", "third"):
        container.get(resource_named(name))

    container.shutdown_resources()

    assert Ledger.events == ["third", "second", "first"]


def test_with_container_tears_down_on_exit():
    container = Container()

    @Service(container=container)
    @Resource
    class Db:
        def close(self) -> None:
            Ledger.record("close")

    with container:
        container.get(Db)
        assert Ledger.events == []
    assert Ledger.events == ["close"]


def test_torn_down_singleton_is_rebuilt_on_next_get():
    container = Container()

    @Service(container=container)
    @Resource
    class Db:
        def close(self) -> None: ...

    first = container.get(Db)
    container.shutdown_resources()
    second = container.get(Db)

    assert first is not second


def test_custom_close_method_name():
    container = Container()

    @Service(container=container)
    @Resource(close="dispose")
    class Pool:
        def dispose(self) -> None:
            Ledger.record("dispose")

    container.get(Pool)
    container.shutdown_resources()

    assert Ledger.events == ["dispose"]


def test_context_manager_protocol_is_entered_and_exited():
    container = Container()

    @Service(container=container)
    @Resource
    class Managed:
        def __enter__(self) -> "Managed":
            Ledger.record("enter")
            return self

        def __exit__(self, *exc: object) -> bool:
            Ledger.record("exit")
            return False

    container.get(Managed)
    assert Ledger.events == ["enter"]
    container.shutdown_resources()
    assert Ledger.events == ["enter", "exit"]


# --- async class form: aclose ---------------------------------------------------


def test_async_close_awaited_by_ashutdown():
    container = Container()

    @Service(container=container)
    @Resource(close="aclose")
    class AsyncClient:
        async def aclose(self) -> None:
            Ledger.record("aclose")

    container.get(AsyncClient)
    asyncio.run(container.ashutdown_resources())

    assert Ledger.events == ["aclose"]


def test_async_resource_rejects_sync_shutdown():
    container = Container()

    @Service(container=container)
    @Resource(close="aclose")
    class AsyncClient:
        async def aclose(self) -> None: ...

    container.get(AsyncClient)

    with pytest.raises(ResourceTeardownError):
        container.shutdown_resources()


def test_async_with_container_awaits_teardown():
    container = Container()

    @Service(container=container)
    @Resource(close="aclose")
    class AsyncClient:
        async def aclose(self) -> None:
            Ledger.record("aclose")

    async def scenario() -> None:
        async with container:
            container.get(AsyncClient)

    asyncio.run(scenario())
    assert Ledger.events == ["aclose"]


# --- function form: generator providers -----------------------------------------


class Config:
    dsn = "sqlite://"


def test_sync_generator_provider_autowires_and_cleans_up():
    container = Container()
    container.register(Config)

    @Resource(container=container)
    def pool(config: Config) -> Iterator[str]:
        Ledger.record(f"open:{config.dsn}")
        yield config.dsn
        Ledger.record("cleanup")

    value = container.get(str)
    assert value == "sqlite://"
    assert Ledger.events == ["open:sqlite://"]

    container.shutdown_resources()
    assert Ledger.events == ["open:sqlite://", "cleanup"]


def test_async_generator_provider_via_aget():
    container = Container()

    @Resource(container=container)
    async def session() -> AsyncIterator[str]:
        Ledger.record("aopen")
        yield "session"
        Ledger.record("aclean")

    async def scenario() -> str:
        async with container:
            return await container.aget(str)

    result = asyncio.run(scenario())
    assert result == "session"
    assert Ledger.events == ["aopen", "aclean"]


def test_async_provider_rejects_sync_get():
    container = Container()

    @Resource(container=container)
    async def session() -> AsyncIterator[str]:
        yield "x"

    with pytest.raises(UnresolvableDependencyError):
        container.get(str)


# --- teardown error aggregation -------------------------------------------------


def test_teardown_errors_are_aggregated_but_every_resource_closed():
    container = Container()

    @Service(container=container)
    @Resource
    class Fine:
        def close(self) -> None:
            Ledger.record("fine")

    @Service(container=container)
    @Resource
    class Boom:
        def close(self) -> None:
            Ledger.record("boom")
            raise RuntimeError("kaboom")

    container.get(Fine)
    container.get(Boom)

    with pytest.raises(ResourceTeardownError):
        container.shutdown_resources()
    assert set(Ledger.events) == {"boom", "fine"}


# --- validation -----------------------------------------------------------------


def test_non_singleton_resource_class_is_rejected():
    container = Container()

    @Resource
    class Db:
        def close(self) -> None: ...

    with pytest.raises(DependencyRegistrationError):
        container.register(Db, scope=Scope.TRANSIENT)


def test_non_generator_resource_function_is_rejected():
    def not_a_generator() -> str:
        return "x"

    with pytest.raises(DependencyRegistrationError):
        provider_spec(not_a_generator)


def test_class_without_teardown_mechanism_is_rejected():
    class Plain:
        pass

    with pytest.raises(DependencyRegistrationError):
        class_resource_spec(Plain, "close")


def test_async_context_manager_class_is_rejected():
    class AsyncManaged:
        async def __aenter__(self) -> "AsyncManaged":
            return self

        async def __aexit__(self, *exc: object) -> bool:
            return False

    with pytest.raises(DependencyRegistrationError):
        class_resource_spec(AsyncManaged, "close")


def test_provider_without_iterator_return_annotation_is_rejected():
    def bad() -> str:  # a generator body, but not annotated as Iterator[...]
        yield "x"  # type: ignore[misc]

    with pytest.raises(DependencyRegistrationError):
        provider_spec(bad)


def test_duplicate_provider_registration_is_rejected():
    container = Container()

    @Resource(container=container)
    def one() -> Iterator[str]:
        yield "a"

    def two() -> Iterator[str]:
        yield "b"

    with pytest.raises(DependencyRegistrationError):
        container.register_provider(provider_spec(two))


def test_transient_provider_is_rejected():
    container = Container()

    def gen() -> Iterator[str]:
        yield "x"

    with pytest.raises(DependencyRegistrationError):
        container.register_provider(provider_spec(gen), scope=Scope.TRANSIENT)


# --- @Resource decorator dispatch -----------------------------------------------


def test_resource_accepts_positional_options():
    container = Container()

    @Service(container=container)
    @Resource(ResourceOptions(close="dispose"))
    class Pool:
        def dispose(self) -> None:
            Ledger.record("dispose")

    container.get(Pool)
    container.shutdown_resources()
    assert Ledger.events == ["dispose"]


def test_resource_rejects_options_and_kwargs_together():
    with pytest.raises(DecoratorConfigurationError):
        Resource(ResourceOptions(), close="dispose")


def test_resource_rejects_non_options_positional():
    with pytest.raises(DecoratorConfigurationError):
        Resource(123)


def test_resource_rejects_multiple_targets():
    class A:
        def close(self) -> None: ...

    class B:
        def close(self) -> None: ...

    with pytest.raises(DecoratorConfigurationError):
        Resource(A, B)


# --- aget fast paths ------------------------------------------------------------


def test_aget_returns_cached_singleton_and_falls_back_to_sync():
    container = Container()
    container.register(Config)

    async def scenario() -> tuple[Config, Config]:
        first = await container.aget(Config)  # sync fallback path
        second = await container.aget(Config)  # warm-cache path
        return first, second

    first, second = asyncio.run(scenario())
    assert first is second


def test_aget_honors_override():
    container = Container()
    container.register(Config)
    stub = Config()
    container.override(Config, stub)

    result = asyncio.run(container.aget(Config))
    assert result is stub


def test_sync_generator_yielding_twice_raises_on_teardown():
    container = Container()

    @Resource(container=container)
    def bad() -> Iterator[str]:
        yield "a"
        yield "b"  # a second yield -> teardown can't advance to StopIteration

    container.get(str)
    with pytest.raises(ResourceTeardownError):
        container.shutdown_resources()


def test_async_generator_yielding_twice_raises_on_teardown():
    container = Container()

    @Resource(container=container)
    async def bad() -> AsyncIterator[str]:
        yield "a"
        yield "b"

    async def scenario() -> None:
        await container.aget(str)
        await container.ashutdown_resources()

    with pytest.raises(ResourceTeardownError):
        asyncio.run(scenario())


def test_ashutdown_aggregates_a_failing_sync_close():
    container = Container()

    @Service(container=container)
    @Resource
    class Boom:
        def close(self) -> None:
            raise RuntimeError("boom")

    container.get(Boom)
    with pytest.raises(ResourceTeardownError):
        asyncio.run(container.ashutdown_resources())


def test_aget_with_an_unrelated_override_still_resolves():
    container = Container()
    container.register(Config)
    container.override(str, "unrelated")  # a non-empty override map, but not for Config

    result = asyncio.run(container.aget(Config))
    assert isinstance(result, Config)


def test_provider_with_unresolvable_return_annotation_is_rejected():
    def provider() -> "Undefined":  # type: ignore[name-defined]  # noqa: F821
        yield 1

    with pytest.raises(DependencyRegistrationError):
        provider_spec(provider)


def test_provider_with_unparameterized_iterator_is_rejected():
    import typing

    def provider() -> typing.Iterator:  # no type argument to say what it yields
        yield 1

    with pytest.raises(DependencyRegistrationError):
        provider_spec(provider)


def test_reset_drops_finalizers_without_running_them():
    container = Container()

    @Service(container=container)
    @Resource
    class Db:
        def close(self) -> None:
            Ledger.record("close")

    container.get(Db)
    container.reset()
    container.shutdown_resources()

    assert Ledger.events == []
