import pytest

pytest.importorskip("sanic")
pytest.importorskip("sanic_testing")

from sanic_testing import TestManager

from examples.di.sanic.app import Greeter, UserRepo, app, container

TestManager(app)  # attaches app.test_client


def test_greet_endpoint_resolves_services():
    container.reset()
    _request, response = app.test_client.get("/greet/1")
    assert response.json == {"message": "Hello, Ada!"}


def test_greet_endpoint_with_overridden_repo():
    class FakeRepo:
        def name(self, user_id: int) -> str:
            return "Mock"

    container.reset()
    container.override(UserRepo, FakeRepo())
    _request, response = app.test_client.get("/greet/1")
    assert response.json == {"message": "Hello, Mock!"}
    container.clear_overrides()


def test_container_resolves_greeter_directly():
    container.reset()
    assert isinstance(container.get(Greeter), Greeter)
