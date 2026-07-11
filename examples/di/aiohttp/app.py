"""Resolve inito services inside aiohttp request handlers.

The services declare dependencies as fields and let inito write the constructor
(`@RequiredArgsConstructor`). Handlers are async; a service is resolved from the
container per request (the warm singleton path is a single dict lookup). DI 2.0
phase 4 will add a per-request scope for request-lifetime objects.

Run:  python -m examples.di.aiohttp.app   (serves on :8080)
"""

from __future__ import annotations

from typing import ClassVar

from aiohttp import web

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


async def greet(request: web.Request) -> web.Response:
    user_id = int(request.match_info["user_id"])
    return web.json_response({"message": container.get(Greeter).greet(user_id)})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/greet/{user_id}", greet)
    return app


if __name__ == "__main__":
    web.run_app(create_app())
