"""Wire a Redis client as a singleton and inject a Cache service that uses it.

`Cache` declares its dependency as a field and lets inito write the constructor
(`@RequiredArgsConstructor`). `RedisClient` keeps a hand-written `__init__`
because it does real work — building the client — which is genuine logic, not
the field-forwarding boilerplate inito removes. (DI 2.0's upcoming `Factory`
provider will let you register the client without even this wrapper.)

Run:  REDIS_URL=redis://localhost:6379/0 python -m examples.di.redis.services
"""

from __future__ import annotations

import redis

from inito import Config, Container, RequiredArgsConstructor, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="REDIS_")
class RedisSettings:
    url: str = "redis://localhost:6379/0"


@Singleton(container=container)
class RedisClient:
    def __init__(self, settings: RedisSettings) -> None:  # real work: build the client
        self.client = redis.Redis.from_url(settings.url, decode_responses=True)


@Service(container=container)
@RequiredArgsConstructor
class Cache:
    redis_client: RedisClient

    def get(self, key: str) -> str | None:
        return self.redis_client.client.get(key)

    def set(self, key: str, value: str) -> None:
        self.redis_client.client.set(key, value)


def main() -> None:
    cache = container.get(Cache)
    cache.set("greeting", "hello from inito")
    print(cache.get("greeting"))


if __name__ == "__main__":
    main()
