"""Wire a Valkey client as a singleton and inject a Cache service that uses it.

Valkey is a Redis fork with a drop-in client, so the wiring is identical to the
redis example. `Cache` lets inito write its constructor
(`@RequiredArgsConstructor`); `ValkeyClient` keeps a hand-written `__init__`
because building the client is real work, not field-forwarding boilerplate.

Run:  VALKEY_URL=valkey://localhost:6379/0 python -m examples.di.valkey.services
"""

from __future__ import annotations

import valkey

from inito import Config, Container, RequiredArgsConstructor, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="VALKEY_")
class ValkeySettings:
    url: str = "valkey://localhost:6379/0"


@Singleton(container=container)
class ValkeyClient:
    def __init__(self, settings: ValkeySettings) -> None:  # real work: build the client
        self.client = valkey.Valkey.from_url(settings.url, decode_responses=True)


@Service(container=container)
@RequiredArgsConstructor
class Cache:
    valkey_client: ValkeyClient

    def get(self, key: str) -> str | None:
        return self.valkey_client.client.get(key)

    def set(self, key: str, value: str) -> None:
        self.valkey_client.client.set(key, value)


def main() -> None:
    cache = container.get(Cache)
    cache.set("greeting", "hello from inito")
    print(cache.get("greeting"))


if __name__ == "__main__":
    main()
