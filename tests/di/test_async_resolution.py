"""aget(): full async resolution — async @Resource providers anywhere in the graph."""

import asyncio
from collections.abc import AsyncIterator

import pytest

from inito.decorators.resource import Resource
from inito.decorators.service import Service
from inito.di.container import Container, Scope
from inito.exceptions.errors import CircularDependencyError, UnresolvableDependencyError


def test_aget_builds_a_graph_with_an_async_provider_dependency():
    container = Container()
    events = []

    @Resource(container=container)
    async def conn() -> AsyncIterator[str]:
        events.append("open")
        yield "dsn://"
        events.append("close")

    class Repo:
        def __init__(self, conn: str) -> None:
            self.conn = conn

    container.register(Repo)

    async def scenario() -> Repo:
        async with container:
            repo = await container.aget(Repo)
            assert repo.conn == "dsn://"
            return repo

    asyncio.run(scenario())
    assert events == ["open", "close"]


def test_aget_caches_the_async_singleton():
    container = Container()

    @Resource(container=container)
    async def conn() -> AsyncIterator[object]:
        yield object()

    async def scenario() -> None:
        async with container:
            first = await container.aget(object)
            second = await container.aget(object)
            assert first is second

    asyncio.run(scenario())


def test_aget_resolves_plain_sync_services():
    container = Container()

    class A:
        pass

    class B:
        def __init__(self, a: A) -> None:
            self.a = a

    container.register(A)
    container.register(B)

    b = asyncio.run(container.aget(B))
    assert isinstance(b.a, A)


def test_aget_resolves_scoped_services():
    container = Container()

    class Session:
        pass

    container.register(Session, scope=Scope.SCOPED)

    async def scenario() -> None:
        async with container.scope():
            assert await container.aget(Session) is await container.aget(Session)

    asyncio.run(scenario())


def test_aget_detects_cycles():
    container = Container()
    container.register(_ACycle)
    container.register(_BCycle)

    with pytest.raises(CircularDependencyError):
        asyncio.run(container.aget(_ACycle))


def test_aget_unregistered_raises():
    container = Container()

    class Nope:
        pass

    with pytest.raises(UnresolvableDependencyError):
        asyncio.run(container.aget(Nope))


def test_aget_honors_override():
    container = Container()

    class Job:
        pass

    stub = Job()
    container.register(Job)
    container.override(Job, stub)

    assert asyncio.run(container.aget(Job)) is stub


def test_aget_async_provider_as_dependency_of_async_service():
    container = Container()

    @Resource(container=container)
    async def client() -> AsyncIterator[str]:
        yield "client"

    @Service(container=container)
    class Api:
        def __init__(self, client: str) -> None:
            self.client = client

    async def scenario() -> None:
        async with container:
            api = await container.aget(Api)
            assert api.client == "client"

    asyncio.run(scenario())


def test_aget_uses_an_override_for_a_nested_dependency():
    container = Container()

    class Dep:
        pass

    class Owner:
        def __init__(self, dep: Dep) -> None:
            self.dep = dep

    container.register(Dep)
    container.register(Owner)
    stub = Dep()
    container.override(Dep, stub)

    owner = asyncio.run(container.aget(Owner))
    assert owner.dep is stub


def test_aget_builds_transient_and_thread_local_services():
    container = Container()

    class Trans:
        pass

    class Local:
        pass

    container.register(Trans, scope=Scope.TRANSIENT)
    container.register(Local, scope=Scope.THREAD_LOCAL)

    async def scenario() -> None:
        assert await container.aget(Trans) is not await container.aget(Trans)
        assert await container.aget(Local) is await container.aget(Local)

    asyncio.run(scenario())


def test_aget_omits_an_unregistered_defaulted_dependency():
    container = Container()

    class Job:
        def __init__(self, tries: int = 3) -> None:
            self.tries = tries

    container.register(Job)
    assert asyncio.run(container.aget(Job)).tries == 3


def test_aget_injects_a_factory_dependency():
    from inito.di.factory import Factory

    container = Container()

    class Widget:
        def __init__(self, title: str) -> None:
            self.title = title

    class Maker:
        def __init__(self, make: Factory[Widget]) -> None:
            self.make = make

    container.register(Maker)
    maker = asyncio.run(container.aget(Maker))
    assert maker.make(title="hi").title == "hi"


def test_aget_resolves_a_qualified_dependency():
    from typing import Annotated

    from inito.di.dependency_resolver import Qualifier

    container = Container()

    class Repo:
        pass

    class Postgres(Repo):
        pass

    class Consumer:
        def __init__(self, repo: Annotated[Repo, Qualifier("pg")]) -> None:
            self.repo = repo

    container.register(Postgres, qualifier="pg")
    container.register(Consumer)
    consumer = asyncio.run(container.aget(Consumer))
    assert isinstance(consumer.repo, Postgres)


def test_aget_resolves_a_sole_registered_implementation():
    container = Container()

    class Base:
        pass

    class Impl(Base):
        pass

    class Consumer:
        def __init__(self, base: Base) -> None:
            self.base = base

    container.register(Impl)
    container.register(Consumer)
    consumer = asyncio.run(container.aget(Consumer))
    assert isinstance(consumer.base, Impl)


class _ACycle:
    def __init__(self, b: "_BCycle") -> None:
        self.b = b


class _BCycle:
    def __init__(self, a: _ACycle) -> None:
        self.a = a
