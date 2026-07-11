# Django integration

A Django view pulls a service from the InitO container and returns a response.
InitO wires your domain/service objects; Django owns models and requests. Tested
with Django's test client, using `container.override(...)` for a fake repo.

```bash
python -m examples.di.django.app runserver
pytest examples/di/django --no-cov
```
