import pytest

from inito import NoArgsConstructor
from inito.decorators.no_args_constructor import NoArgsConstructorOptions
from inito.exceptions.errors import DecoratorConfigurationError, InvalidFieldDefinitionError


def test_no_args_constructor_uses_field_defaults():
    @NoArgsConstructor
    class User:
        name: str = "anonymous"
        age: int = 0

    user = User()
    assert user.name == "anonymous"
    assert user.age == 0


def test_no_args_constructor_raises_when_a_field_has_no_default():
    with pytest.raises(InvalidFieldDefinitionError):

        @NoArgsConstructor
        class User:
            name: str


def test_no_args_constructor_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        NoArgsConstructor("not a class")


def test_no_args_constructor_options_is_empty_and_equatable():
    assert NoArgsConstructorOptions() == NoArgsConstructorOptions()
