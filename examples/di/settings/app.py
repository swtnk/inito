"""Configuration injection: load settings from the environment, autowire by type.

Run:  APP_DATABASE_URL=postgres://db APP_PORT=9000 python -m examples.di.settings.app
"""

from __future__ import annotations

from inito import Config, Container, Service

container = Container()


@Service(container=container)
@Config(prefix="APP_")
class Settings:
    database_url: str = "sqlite:///app.db"
    port: int = 8000
    debug: bool = False


@Service(container=container)
class Report:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def describe(self) -> str:
        return (
            f"database_url={self.settings.database_url} "
            f"port={self.settings.port} debug={self.settings.debug}"
        )


def main() -> None:
    print(container.get(Report).describe())


if __name__ == "__main__":
    main()
