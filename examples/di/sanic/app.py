"""Resolve inito services inside Sanic request handlers.

The services declare dependencies as fields and let inito write the constructor
(`@RequiredArgsConstructor`). Handlers are async; the service is resolved from
the container per request.

Run:  sanic examples.di.sanic.app:app
"""

from __future__ import annotations

from typing import ClassVar

from sanic import Sanic, json
from sanic.request import Request
from sanic.response import JSONResponse

from inito import Config, Container, RequiredArgsConstructor, Service, Singleton

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
    settings: Settings
    repo: UserRepo

    def greet(self, user_id: int) -> str:
        return f"{self.settings.greeting}, {self.repo.name(user_id) or 'stranger'}!"


app = Sanic("inito_example")


@app.get("/greet/<user_id:int>")
async def greet(request: Request, user_id: int) -> JSONResponse:
    return json({"message": container.get(Greeter).greet(user_id)})
