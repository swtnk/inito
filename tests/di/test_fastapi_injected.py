"""Injected[T]: FastAPI dependency resolving from a Container, tested with a fake fastapi."""

import asyncio
import sys
import types
import typing

import pytest

from inito.decorators.resource import Resource
from inito.decorators.service import Service
from inito.di.container import Container, Scope
from inito.di.integrations.fastapi import Injected


@pytest.fixture
def fake_depends(monkeypatch):
    """Install a duck-typed ``fastapi`` module so tests need no real FastAPI install."""
    module = types.ModuleType("fastapi")

    class Depends:
        def __init__(self, dependency):
            self.dependency = dependency

    module.Depends = Depends  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "fastapi", module)
    return Depends


def test_injected_subscript_returns_annotated_depends(fake_depends):
    class Widget:
        pass

    annotation = Injected[Widget]
    target, marker = typing.get_args(annotation)

    assert target is Widget
    assert isinstance(marker, fake_depends)


def test_injected_call_form_returns_depends(fake_depends):
    class Widget:
        pass

    container = Container()
    container.register(Widget)

    marker = Injected(Widget, container=container)
    assert isinstance(marker, fake_depends)


def test_injected_opens_a_scope_and_tears_it_down_per_request(fake_depends):
    container = Container()
    events = []

    @Service(container=container, scope=Scope.SCOPED)
    @Resource
    class Conn:
        def close(self) -> None:
            events.append("close")

    marker = Injected(Conn, container=container)

    async def request() -> None:
        provider = marker.dependency()  # the async-generator FastAPI dependency
        conn = await provider.__anext__()
        assert isinstance(conn, Conn)  # a scope was opened (Conn is SCOPED)
        assert events == []
        with pytest.raises(StopAsyncIteration):
            await provider.__anext__()  # request ends -> scope tears down

    asyncio.run(request())
    assert events == ["close"]


def test_injected_resolves_a_singleton_service(fake_depends):
    container = Container()

    @Service(container=container)
    class Repo:
        pass

    marker = Injected(Repo, container=container)

    async def request() -> Repo:
        provider = marker.dependency()
        value = await provider.__anext__()
        with pytest.raises(StopAsyncIteration):
            await provider.__anext__()
        return value

    resolved = asyncio.run(request())
    assert resolved is container.get(Repo)
