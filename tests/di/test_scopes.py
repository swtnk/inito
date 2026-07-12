"""Scope.SCOPED and container.scope(): per-scope instances and scoped resource teardown."""

import asyncio

import pytest

from inito.decorators.resource import Resource
from inito.decorators.service import Service
from inito.di.container import Container, Scope
from inito.exceptions.errors import DependencyRegistrationError, ResourceTeardownError, ScopeError


class Session:
    pass


def test_scoped_service_is_one_instance_per_scope():
    container = Container()
    container.register(Session, scope=Scope.SCOPED)

    with container.scope():
        first = container.get(Session)
        second = container.get(Session)
        assert first is second


def test_scoped_service_is_distinct_across_scopes():
    container = Container()
    container.register(Session, scope=Scope.SCOPED)

    with container.scope():
        a = container.get(Session)
    with container.scope():
        b = container.get(Session)

    assert a is not b


def test_scoped_service_without_active_scope_raises():
    container = Container()
    container.register(Session, scope=Scope.SCOPED)

    with pytest.raises(ScopeError):
        container.get(Session)


def test_scopes_nest_independently():
    container = Container()
    container.register(Session, scope=Scope.SCOPED)

    with container.scope():
        outer = container.get(Session)
        with container.scope():
            inner = container.get(Session)
            assert inner is not outer
        # back in the outer scope, the outer instance is still cached
        assert container.get(Session) is outer


def test_scoped_resource_torn_down_at_scope_exit_not_container_shutdown():
    container = Container()
    events = []

    @Service(container=container, scope=Scope.SCOPED)
    @Resource
    class Conn:
        def close(self) -> None:
            events.append("close")

    with container.scope():
        container.get(Conn)
        assert events == []
    assert events == ["close"]  # closed on scope exit

    container.shutdown_resources()  # nothing scope-owned remains
    assert events == ["close"]


def test_scoped_resources_torn_down_lifo():
    container = Container()
    events = []

    def scoped_resource(name: str) -> type:
        @Service(container=container, scope=Scope.SCOPED)
        @Resource
        class Res:
            def close(self) -> None:
                events.append(name)

        return Res

    a, b = scoped_resource("a"), scoped_resource("b")
    with container.scope():
        container.get(a)
        container.get(b)
    assert events == ["b", "a"]


def test_async_scoped_resource_torn_down_at_async_scope_exit():
    container = Container()
    events = []

    @Service(container=container, scope=Scope.SCOPED)
    @Resource(close="aclose")
    class AsyncConn:
        async def aclose(self) -> None:
            events.append("aclose")

    async def scenario() -> None:
        async with container.scope():
            await container.aget(AsyncConn)
            assert events == []
        assert events == ["aclose"]

    asyncio.run(scenario())


def test_sync_scope_exit_with_async_resource_raises():
    container = Container()

    @Service(container=container, scope=Scope.SCOPED)
    @Resource(close="aclose")
    class AsyncConn:
        async def aclose(self) -> None: ...

    with pytest.raises(ResourceTeardownError), container.scope():
        container.get(AsyncConn)


def test_transient_resource_is_still_rejected():
    container = Container()

    @Resource
    class Conn:
        def close(self) -> None: ...

    with pytest.raises(DependencyRegistrationError):
        container.register(Conn, scope=Scope.TRANSIENT)
