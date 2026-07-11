import pytest

pytest.importorskip("redis")

from examples.di.redis.services import Cache, RedisClient, container


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value


class _FakeRedisClient:
    def __init__(self) -> None:
        self.client = _FakeRedis()


def test_cache_wiring_resolves():
    # The real redis client is constructed (lazily - no connection); the DI graph
    # resolves end to end.
    container.reset()
    assert isinstance(container.get(Cache), Cache)


def test_cache_roundtrip_with_an_overridden_client():
    container.reset()
    container.override(RedisClient, _FakeRedisClient())
    cache = container.get(Cache)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    container.clear_overrides()
