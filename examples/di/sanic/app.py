"""Resolve inito services inside Sanic request handlers.

Handlers are async; the service is resolved from the container per request.

Run:  sanic examples.di.sanic.app:app
"""

from __future__ import annotations

from sanic import Sanic, json
from sanic.request import Request
from sanic.response import JSONResponse

from inito import Config, Container, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="APP_")
class Settings:
    greeting: str = "Hello"


@Singleton(container=container)
class UserRepo:
    def __init__(self) -> None:
        self._names = {1: "Ada", 2: "Linus"}

    def name(self, user_id: int) -> str | None:
        return self._names.get(user_id)


@Service(container=container)
class Greeter:
    def __init__(self, settings: Settings, repo: UserRepo) -> None:
        self._settings = settings
        self._repo = repo

    def greet(self, user_id: int) -> str:
        return f"{self._settings.greeting}, {self._repo.name(user_id) or 'stranger'}!"


app = Sanic("inito_example")


@app.get("/greet/<user_id:int>")
async def greet(request: Request, user_id: int) -> JSONResponse:
    return json({"message": container.get(Greeter).greet(user_id)})
