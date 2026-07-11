"""Wire a Redis client as a singleton and inject a Cache service that uses it.

Run:  REDIS_URL=redis://localhost:6379/0 python -m examples.di.redis.services
"""

from __future__ import annotations

import redis

from inito import Config, Container, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="REDIS_")
class RedisSettings:
    url: str = "redis://localhost:6379/0"


@Singleton(container=container)
class RedisClient:
    def __init__(self, settings: RedisSettings) -> None:
        self.client = redis.Redis.from_url(settings.url, decode_responses=True)


@Service(container=container)
class Cache:
    def __init__(self, redis_client: RedisClient) -> None:
        self._client = redis_client.client

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
