import pytest

pytest.importorskip("pika")

from examples.di.rabbitmq.services import Publisher, RabbitConnection, container


class _FakeChannel:
    def __init__(self) -> None:
        self.declared: list[str] = []
        self.published: list[tuple[str, bytes]] = []

    def queue_declare(self, queue):
        self.declared.append(queue)

    def basic_publish(self, exchange, routing_key, body):
        self.published.append((routing_key, body))


class _FakeConnection:
    def __init__(self) -> None:
        self.last_channel = _FakeChannel()

    def channel(self):
        return self.last_channel


def test_publisher_wiring_resolves():
    # RabbitConnection is built from URL parameters only - no broker needed.
    container.reset()
    assert isinstance(container.get(Publisher), Publisher)


def test_publish_uses_the_connection_channel():
    fake = _FakeConnection()
    container.reset()
    container.override(RabbitConnection, fake)
    container.get(Publisher).publish("greetings", "hi")
    assert fake.last_channel.declared == ["greetings"]
    assert fake.last_channel.published == [("greetings", b"hi")]
    container.clear_overrides()
