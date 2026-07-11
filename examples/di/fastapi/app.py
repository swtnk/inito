"""Wire inito services into FastAPI routes via a Depends bridge to the container.

The service classes below declare their dependencies as fields and let inito
write the constructor (`@RequiredArgsConstructor`) — no hand-written
`def __init__(self, ...)`. The ``provide()`` helper turns any registered service
into a FastAPI dependency (``Depends``). A future ``Injected[T]`` helper
(DI 2.0 phase 4) will make this a one-liner and add per-request scope.

Run:  uvicorn examples.di.fastapi.app:app
"""

from __future__ import annotations

from typing import Any, ClassVar, TypeVar

from fastapi import Depends, FastAPI

from inito import Config, Container, RequiredArgsConstructor, Service, Singleton

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


app = FastAPI()


@app.get("/greet/{user_id}")
def greet(user_id: int, greeter: Greeter = provide(Greeter)) -> dict[str, str]:
    return {"message": greeter.greet(user_id)}
