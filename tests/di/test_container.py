from typing import Optional

import pytest

from inito.di.container import Container, Scope
from inito.exceptions.errors import (
    CircularDependencyError,
    DependencyRegistrationError,
    UnresolvableDependencyError,
)


class Repo:
    pass


# Forward-ref-based cycles must be module-level classes: get_type_hints resolves
# string annotations against the class's module globals, not an enclosing
# function's locals (same constraint as tests/integration/test_edge_cases.py's
# forward-reference tests).
class _CycleA2:
    def __init__(self, b: "_CycleB2"):
        self.b = b


class _CycleB2:
    def __init__(self, a: _CycleA2):
        self.a = a


class _CycleA3:
    def __init__(self, b: "_CycleB3"):
        self.b = b


class _CycleB3:
    def __init__(self, c: "_CycleC3"):
        self.c = c


class _CycleC3:
    def __init__(self, a: _CycleA3):
        self.a = a


def test_register_and_get_roundtrip():
    container = Container()
    container.register(Repo)
    assert isinstance(container.get(Repo), Repo)


def test_get_unregistered_type_raises_unresolvable():
    container = Container()
    with pytest.raises(UnresolvableDependencyError):
        container.get(Repo)


def test_register_duplicate_raises():
    container = Container()
    container.register(Repo)
    with pytest.raises(DependencyRegistrationError):
        container.register(Repo)


def test_singleton_scope_caches_instance():
    container = Container()
    container.register(Repo, scope=Scope.SINGLETON)
    assert container.get(Repo) is container.get(Repo)


def test_transient_scope_returns_new_instance_each_call():
    container = Container()
    container.register(Repo, scope=Scope.TRANSIENT)
    assert container.get(Repo) is not container.get(Repo)


def test_resolves_nested_dependency_graph_bottom_up():
    class C:
        pass

    class B:
        def __init__(self, c: C):
            self.c = c

    class A:
        def __init__(self, b: B):
            self.b = b

    container = Container()
    container.register(C)
    container.register(B)
    container.register(A)
    a = container.get(A)
    assert isinstance(a, A)
    assert isinstance(a.b, B)
    assert isinstance(a.b.c, C)


def test_circular_dependency_two_nodes_raises():
    container = Container()
    container.register(_CycleA2)
    container.register(_CycleB2)
    with pytest.raises(CircularDependencyError):
        container.get(_CycleA2)


def test_circular_dependency_three_nodes_raises():
    container = Container()
    container.register(_CycleA3)
    container.register(_CycleB3)
    container.register(_CycleC3)
    with pytest.raises(CircularDependencyError):
        container.get(_CycleA3)


def test_self_cycle_raises():
    class A:
        def __init__(self, a: "A"):
            self.a = a

    container = Container()
    container.register(A)
    with pytest.raises(CircularDependencyError):
        container.get(A)


def test_transient_dependency_of_singleton_shares_one_instance():
    class C:
        pass

    class B:
        def __init__(self, c: C):
            self.c = c

    container = Container()
    container.register(C, scope=Scope.TRANSIENT)
    container.register(B, scope=Scope.SINGLETON)
    b1 = container.get(B)
    b2 = container.get(B)
    assert b1 is b2
    assert b1.c is b2.c


def test_unregistered_dependency_with_default_falls_back_to_constructor_default():
    class Sample:
        def __init__(self, port: int = 5432):
            self.port = port

    container = Container()
    container.register(Sample)
    assert container.get(Sample).port == 5432


def test_unregistered_dependency_without_default_raises():
    class Sample:
        def __init__(self, host: str):
            self.host = host

    container = Container()
    container.register(Sample)
    with pytest.raises(UnresolvableDependencyError):
        container.get(Sample)


def test_optional_typed_registered_dependency_still_autowires():
    class Config:
        pass

    class Sample:
        def __init__(self, config: Optional[Config] = None):
            self.config = config

    container = Container()
    container.register(Config)
    container.register(Sample)
    assert isinstance(container.get(Sample).config, Config)


def test_unannotated_constructor_parameter_raises_at_registration_time():
    class Sample:
        def __init__(self, value):
            self.value = value

    container = Container()
    with pytest.raises(DependencyRegistrationError):
        container.register(Sample)


def test_reset_clears_singleton_cache_but_not_registrations():
    container = Container()
    container.register(Repo)
    instance = container.get(Repo)
    container.reset()
    assert container.is_registered(Repo)
    assert container.get(Repo) is not instance


def test_is_registered():
    container = Container()
    assert not container.is_registered(Repo)
    container.register(Repo)
    assert container.is_registered(Repo)


def test_container_instances_are_independent():
    a, b = Container(), Container()
    a.register(Repo)
    assert a.is_registered(Repo)
    assert not b.is_registered(Repo)
