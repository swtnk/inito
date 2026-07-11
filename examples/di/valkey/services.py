"""Wire a Valkey client as a singleton and inject a Cache service that uses it.

Valkey is a Redis fork with a drop-in client, so the wiring is identical to the
redis example - only the client class and URL change.

Run:  VALKEY_URL=valkey://localhost:6379/0 python -m examples.di.valkey.services
"""

from __future__ import annotations

import valkey

from inito import Config, Container, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="VALKEY_")
class ValkeySettings:
    url: str = "valkey://localhost:6379/0"


@Singleton(container=container)
class ValkeyClient:
    def __init__(self, settings: ValkeySettings) -> None:
        self.client = valkey.Valkey.from_url(settings.url, decode_responses=True)


@Service(container=container)
class Cache:
    def __init__(self, valkey_client: ValkeyClient) -> None:
        self._client = valkey_client.client

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str) -> None:
        self._client.set(key, value)


def main() -> None:
    cache = container.get(Cache)
    cache.set("greeting", "hello from inito")
    print(cache.get("greeting"))


if __name__ == "__main__":
    main()
