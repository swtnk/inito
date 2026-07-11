import pytest

pytest.importorskip("valkey")

from examples.di.valkey.services import Cache, ValkeyClient, container


class _FakeValkey:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value


class _FakeValkeyClient:
    def __init__(self) -> None:
        self.client = _FakeValkey()


def test_cache_wiring_resolves():
    container.reset()
    assert isinstance(container.get(Cache), Cache)


def test_cache_roundtrip_with_an_overridden_client():
    container.reset()
    container.override(ValkeyClient, _FakeValkeyClient())
    cache = container.get(Cache)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    container.clear_overrides()
