import pytest

from inito import RequiredArgsConstructor
from inito.decorators.required_args_constructor import RequiredArgsConstructorOptions
from inito.exceptions.errors import DecoratorConfigurationError


def test_required_args_constructor_accepts_only_required_fields():
    @RequiredArgsConstructor
    class User:
        name: str
        age: int = 0

    user = User("Ada")
    assert user.name == "Ada"
    assert user.age == 0


def test_required_args_constructor_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        RequiredArgsConstructor("not a class")


def test_required_args_constructor_options_is_empty_and_equatable():
    assert RequiredArgsConstructorOptions() == RequiredArgsConstructorOptions()
