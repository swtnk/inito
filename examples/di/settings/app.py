"""Configuration injection: load settings from the environment, autowire by type.

`Settings` is loaded from the environment by `@Config`; `Report` declares its
dependency as a field and lets inito write the constructor
(`@RequiredArgsConstructor`) — no hand-written `def __init__(self, ...)`.

Run:  APP_DATABASE_URL=postgres://db APP_PORT=9000 python -m examples.di.settings.app
"""

from __future__ import annotations

from inito import Config, Container, RequiredArgsConstructor, Service

container = Container()


@Service(container=container)
@Config(prefix="APP_")
class Settings:
    database_url: str = "sqlite:///app.db"
    port: int = 8000
    debug: bool = False


@Service(container=container)
@RequiredArgsConstructor
class Report:
    settings: Settings

    def describe(self) -> str:
        return (
            f"database_url={self.settings.database_url} "
            f"port={self.settings.port} debug={self.settings.debug}"
        )


def main() -> None:
    print(container.get(Report).describe())


if __name__ == "__main__":
    main()
