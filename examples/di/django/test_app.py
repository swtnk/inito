import json

import pytest

pytest.importorskip("django")

from django.test import Client

from examples.di.django.app import Greeter, UserRepo, container


def test_greet_view_resolves_services():
    container.reset()
    response = Client().get("/greet/1")
    assert response.status_code == 200
    assert json.loads(response.content) == {"message": "Hello, Ada!"}


def test_greet_view_with_overridden_repo():
    class FakeRepo:
        def name(self, user_id: int) -> str:
            return "Mock"

    container.reset()
    container.override(UserRepo, FakeRepo())
    response = Client().get("/greet/1")
    assert json.loads(response.content) == {"message": "Hello, Mock!"}
    container.clear_overrides()


def test_container_resolves_greeter_directly():
    container.reset()
    assert isinstance(container.get(Greeter), Greeter)
