import pytest

from inito import Singleton
from inito.di.container import Scope, default_container
from inito.exceptions.errors import DecoratorConfigurationError


def test_singleton_registers_as_singleton_scope():
    @Singleton
    class Repo:
        pass

    assert default_container.is_registered(Repo)
    assert default_container.get(Repo) is default_container.get(Repo)


def test_singleton_call_form_also_registers_as_singleton():
    @Singleton()
    class Repo:
        pass

    assert default_container.get(Repo) is default_container.get(Repo)


def test_singleton_rejects_explicit_scope_kwarg():
    with pytest.raises(DecoratorConfigurationError):

        @Singleton(scope=Scope.TRANSIENT)
        class Repo:
            pass
