"""Wire inito services into FastAPI routes via a Depends bridge to the container.

The ``provide()`` helper turns any registered service into a FastAPI dependency
(``Depends``), so routes stay ordinary FastAPI functions. A future ``Injected[T]``
helper (DI 2.0 phase 4) will make this a one-liner and add per-request scope.

Run:  uvicorn examples.di.fastapi.app:app
"""

from __future__ import annotations

from typing import Any, TypeVar

from fastapi import Depends, FastAPI

from inito import Config, Container, Service, Singleton

container = Container()

T = TypeVar("T")


def provide(service_type: type[T]) -> Any:
    """A FastAPI dependency resolving service_type from the inito container."""

    def _resolve() -> T:
        return container.get(service_type)

    return Depends(_resolve)


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


app = FastAPI()


@app.get("/greet/{user_id}")
def greet(user_id: int, greeter: Greeter = provide(Greeter)) -> dict[str, str]:
    return {"message": greeter.greet(user_id)}
