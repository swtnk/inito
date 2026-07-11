import asyncio

import pytest

pytest.importorskip("aiohttp")

from aiohttp.test_utils import TestClient, TestServer

from examples.di.aiohttp.app import Greeter, Settings, UserRepo, container, create_app


async def _get_json(app, path):
    async with TestClient(TestServer(app)) as client:
        response = await client.get(path)
        return await response.json()


def test_greet_endpoint_resolves_services():
    container.reset()
    result = asyncio.run(_get_json(create_app(), "/greet/1"))
    assert result == {"message": "Hello, Ada!"}


def test_greet_endpoint_with_overridden_repo():
    class FakeRepo:
        def name(self, user_id: int) -> str:
            return "Mock"

    container.reset()
    container.override(UserRepo, FakeRepo())
    result = asyncio.run(_get_json(create_app(), "/greet/1"))
    assert result == {"message": "Hello, Mock!"}
    container.clear_overrides()


def test_container_resolves_greeter_directly():
    container.reset()
    assert isinstance(container.get(Greeter), Greeter)
    assert isinstance(container.get(Settings), Settings)
