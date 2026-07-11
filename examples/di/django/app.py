"""Resolve inito services inside a Django view.

inito wires your domain/service objects — declared as fields, with the
constructor written by `@RequiredArgsConstructor` — while Django owns models and
requests. The view pulls a service from the container and returns a response;
the same pattern scales to class-based views and DRF.

Run:  python -m examples.di.django.app runserver
"""

from __future__ import annotations

import sys
from typing import ClassVar

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.urls import path

from inito import Config, Container, RequiredArgsConstructor, Service, Singleton

if not settings.configured:
    settings.configure(
        DEBUG=True,
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
        SECRET_KEY="example-only-not-a-secret",
        DATABASES={},
        INSTALLED_APPS=[],
        MIDDLEWARE=[],
    )

container = Container()


@Service(container=container)
@Config(prefix="APP_")
class Settings:
    greeting: str = "Hello"


@Singleton(container=container)
class UserRepo:
    _NAMES: ClassVar[dict[int, str]] = {1: "Ada", 2: "Linus"}

    def name(self, user_id: int) -> str | None:
        return self._NAMES.get(user_id)


@Service(container=container)
@RequiredArgsConstructor
class Greeter:
    config: Settings
    repo: UserRepo

    def greet(self, user_id: int) -> str:
        return f"{self.config.greeting}, {self.repo.name(user_id) or 'stranger'}!"


def greet(request: HttpRequest, user_id: int) -> JsonResponse:
    return JsonResponse({"message": container.get(Greeter).greet(user_id)})


urlpatterns = [path("greet/<int:user_id>", greet)]


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
