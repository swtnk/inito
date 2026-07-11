import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from examples.di.fastapi.app import UserRepo, app, container


def test_greet_endpoint_resolves_services_through_the_container():
    container.reset()
    client = TestClient(app)
    assert client.get("/greet/1").json() == {"message": "Hello, Ada!"}
    assert client.get("/greet/99").json() == {"message": "Hello, stranger!"}


def test_endpoint_with_an_overridden_repo():
    class FakeRepo:
        def name(self, user_id: int) -> str:
            return "Mock"

    container.reset()
    container.override(UserRepo, FakeRepo())
    client = TestClient(app)
    assert client.get("/greet/1").json() == {"message": "Hello, Mock!"}
    container.clear_overrides()
