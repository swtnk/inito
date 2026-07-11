"""Resolve inito services inside aiohttp request handlers.

Handlers are async; a service is resolved from the container per request (the
warm singleton path is a single dict lookup). DI 2.0 phase 4 will add a
per-request scope for request-lifetime objects.

Run:  python -m examples.di.aiohttp.app   (serves on :8080)
"""

from __future__ import annotations

from aiohttp import web

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


async def greet(request: web.Request) -> web.Response:
    user_id = int(request.match_info["user_id"])
    greeter = container.get(Greeter)
    return web.json_response({"message": greeter.greet(user_id)})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/greet/{user_id}", greet)
    return app


if __name__ == "__main__":
    web.run_app(create_app())
