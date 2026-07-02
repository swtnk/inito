"""Interoperability tests: inito composed with popular Python frameworks.

These verify the claims that back "use inito in any kind of project": that the
additive decorators (@Getter/@Setter/@ToString/@EqualsAndHashCode) compose with
framework model base classes, that @Builder(use_init=True) constructs through a
framework's own validating constructor, and that the dependency-injection layer
is safe to drive from async request handlers (FastAPI/Sanic/Starlette style).

Every framework is optional: each test importorskips it and imports it inside
the test body, so collection succeeds without the `interop` extra installed.
They run in a dedicated CI job on a stable interpreter (see .github/workflows).

Note: this module deliberately does *not* use ``from __future__ import
annotations``. inito's DI resolves constructor type hints at runtime, and these
tests define their services locally inside each test function; stringized
annotations would be evaluated against the module globals, where those local
names are invisible. Real projects register module-level services, so this is a
test-authoring constraint, not a library limitation.
"""

import asyncio

import pytest

from inito import (
    Builder,
    EqualsAndHashCode,
    Getter,
    Inject,
    Service,
    Setter,
    Singleton,
    ToString,
    default_container,
)

# --- Pydantic v2 ------------------------------------------------------------


def test_additive_decorators_on_a_pydantic_model():
    pytest.importorskip("pydantic")
    from pydantic import BaseModel

    @Getter
    @ToString
    class Settings(BaseModel):
        host: str = "localhost"
        port: int = 5432

    settings = Settings()
    assert settings.get_host() == "localhost"
    assert settings.get_port() == 5432
    assert repr(settings) == "Settings(host='localhost', port=5432)"


def test_builder_use_init_runs_pydantic_validation():
    pydantic = pytest.importorskip("pydantic")
    from pydantic import BaseModel

    @Builder(use_init=True)
    class User(BaseModel):
        name: str
        age: int = 0  # a Pydantic default inito cannot see

    user = User.builder().name("Ada").build()  # age omitted -> Pydantic default
    assert user.name == "Ada"
    assert user.age == 0
    # Fully-initialised model: fields_set tracks exactly what the builder set.
    assert user.__pydantic_fields_set__ == {"name"}

    with pytest.raises(pydantic.ValidationError):
        User.builder().name("Ada").age("not-an-int").build()


def test_default_builder_bypasses_pydantic_validation_as_documented():
    # The fast default build() intentionally bypasses __init__; on a validating
    # model that means no validation runs. This is the documented reason
    # use_init=True exists, pinned here so the tradeoff can't silently change.
    pytest.importorskip("pydantic")
    from pydantic import BaseModel

    @Builder
    class User(BaseModel):
        name: str
        age: int

    built = User.builder().name("Ada").age(30).build()
    assert (built.name, built.age) == ("Ada", 30)
    assert not hasattr(built, "__pydantic_fields_set__")  # ctor never ran


# --- SQLAlchemy 2.0 declarative --------------------------------------------


def test_builder_use_init_and_repr_on_sqlalchemy_model():
    pytest.importorskip("sqlalchemy")
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    class Base(DeclarativeBase):
        pass

    @ToString
    @Builder(use_init=True)
    class Widget(Base):
        __tablename__ = "widget_interop"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column()

    widget = Widget.builder().id(1).name("gadget").build()
    assert (widget.id, widget.name) == (1, "gadget")
    # Constructed through SQLAlchemy's declarative __init__ -> real instrumentation.
    assert hasattr(widget, "_sa_instance_state")
    assert repr(widget) == "Widget(id=1, name='gadget')"


# --- Django -----------------------------------------------------------------


def test_inito_decorators_work_within_a_configured_django_process():
    django = pytest.importorskip("django")
    from django.conf import settings

    if not settings.configured:
        settings.configure(INSTALLED_APPS=[], DATABASES={})
        django.setup()

    # inito targets plain domain/DTO/service objects in a Django app (ORM
    # models declare fields as descriptors, not annotations, so they are out of
    # scope by design). Additive decorators on such a class must work normally.
    @Getter
    @Setter
    @ToString
    @EqualsAndHashCode
    class DomainUser:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    user = DomainUser("Ada", 30)
    assert user.get_name() == "Ada"
    user.set_age(31)
    assert user.get_age() == 31
    assert user == DomainUser("Ada", 31)
    assert repr(user) == "DomainUser(name='Ada', age=31)"


# --- Metaclass mechanics (framework-agnostic) -------------------------------


def test_decorators_attach_through_a_custom_metaclass():
    # Django/SQLAlchemy/Pydantic all build classes via a non-trivial metaclass.
    # inito attaches generated methods with setattr on the class object, which
    # must work regardless of the metaclass.
    class TrackingMeta(type):
        pass

    @Getter
    @ToString
    class Model(metaclass=TrackingMeta):
        value: int

        def __init__(self, value: int) -> None:
            self.value = value

    instance = Model(7)
    assert instance.get_value() == 7
    assert repr(instance) == "Model(value=7)"


# --- Async dependency injection (FastAPI / Sanic / Starlette) ---------------


def test_di_container_is_safe_and_stable_under_async_resolution():
    @Singleton
    class Repo:
        def __init__(self) -> None:
            self.answer = 42

    @Service
    class Greeter:
        def __init__(self, repo: Repo) -> None:
            self.repo = repo

    @Inject
    async def handler(service: Greeter) -> int:
        await asyncio.sleep(0)
        return service.repo.answer

    async def run() -> list[int]:
        return await asyncio.gather(*(handler() for _ in range(50)))

    results = asyncio.run(run())

    assert results == [42] * 50
    # The singleton resolved during the concurrent burst is a single instance.
    assert default_container.get(Repo) is default_container.get(Repo)


def test_inject_on_async_handler_still_honours_explicit_arguments():
    @Singleton
    class Repo:
        def __init__(self) -> None:
            self.answer = 42

    @Inject
    async def handler(repo: Repo) -> int:
        return repo.answer

    class FakeRepo:
        answer = 99

    # An explicitly-passed argument is never overridden by the container.
    assert asyncio.run(handler(FakeRepo())) == 99  # type: ignore[arg-type]
