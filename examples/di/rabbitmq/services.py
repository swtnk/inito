"""Wire a RabbitMQ connection as a singleton and inject a Publisher service.

The connection object holds only parameters (no socket) until a channel is
opened, so the graph resolves without a live broker; publishing opens a channel
on demand.

Run:  RABBITMQ_URL=amqp://guest:guest@localhost/ python -m examples.di.rabbitmq.services
"""

from __future__ import annotations

import pika

from inito import Config, Container, Service, Singleton

container = Container()


@Service(container=container)
@Config(prefix="RABBITMQ_")
class RabbitSettings:
    url: str = "amqp://guest:guest@localhost/"


@Singleton(container=container)
class RabbitConnection:
    def __init__(self, settings: RabbitSettings) -> None:
        self._params = pika.URLParameters(settings.url)  # no socket opened here

    def channel(self) -> pika.channel.Channel:
        return pika.BlockingConnection(self._params).channel()


@Service(container=container)
class Publisher:
    def __init__(self, connection: RabbitConnection) -> None:
        self._connection = connection

    def publish(self, queue: str, message: str) -> None:
        channel = self._connection.channel()
        channel.queue_declare(queue=queue)
        channel.basic_publish(exchange="", routing_key=queue, body=message.encode())


def main() -> None:
    container.get(Publisher).publish("greetings", "hello from inito")


if __name__ == "__main__":
    main()
