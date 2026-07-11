# RabbitMQ (pika) injection

A `RabbitConnection` `@Singleton` (built from `@Config` URL settings — parameters
only, no socket until a channel opens) is injected into a `Publisher` service.

```bash
RABBITMQ_URL=amqp://guest:guest@localhost/ python -m examples.di.rabbitmq.services
pytest examples/di/rabbitmq --no-cov    # overrides the connection with a fake — no broker needed
```
