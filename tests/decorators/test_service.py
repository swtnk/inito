import pytest

from inito import RequiredArgsConstructor, Service
from inito.decorators.service import Component, ServiceOptions, service
from inito.di.container import Container, Scope, default_container
from inito.exceptions.errors import DecoratorConfigurationError


def test_bare_service_registers_in_default_container():
    @Service
    class Repo:
        pass

    assert default_container.is_registered(Repo)
    assert isinstance(default_container.get(Repo), Repo)


def test_service_decorated_class_is_still_directly_constructible():
    @Service
    class Point:
        def __init__(self, x: int = 0, y: int = 0):
            self.x, self.y = x, y

    point = Point(1, 2)
    assert (point.x, point.y) == (1, 2)


def test_service_stacked_on_required_args_constructor_autowires():
    # Regression test: @RequiredArgsConstructor's generated __init__ carries
    # no annotations in its own source, so @Service must fall back to the
    # ClassMetadata @RequiredArgsConstructor already cached on the class.
    @Service
    @RequiredArgsConstructor
    class Helper:
        def greet(self, name: str) -> str:
            return f"Hello, {name}!"

    @Service
    @RequiredArgsConstructor
    class MyClass:
        helper: Helper

        def greet_person(self, name: str) -> str:
            return self.helper.greet(name)

    my_class = MyClass(helper=Helper())
    assert my_class.greet_person("Alice") == "Hello, Alice!"

    resolved = default_container.get(MyClass)
    assert resolved.greet_person("Bob") == "Hello, Bob!"


def test_service_with_explicit_container_option():
    custom = Container()

    @Service(container=custom)
    class Repo:
        pass

    assert custom.is_registered(Repo)
    assert not default_container.is_registered(Repo)


def test_service_with_explicit_scope_option():
    custom = Container()

    @Service(scope=Scope.TRANSIENT, container=custom)
    class Repo:
        pass

    assert custom.get(Repo) is not custom.get(Repo)


def test_service_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        Service("not a class")


def test_service_options_defaults():
    assert ServiceOptions() == ServiceOptions(scope=Scope.SINGLETON, container=None)


def test_component_is_alias_for_service():
    assert Component is Service
    assert service is Service
