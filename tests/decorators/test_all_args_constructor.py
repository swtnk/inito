import pytest

from inito import AllArgsConstructor
from inito.decorators.all_args_constructor import AllArgsConstructorOptions
from inito.exceptions.errors import DecoratorConfigurationError


def test_all_args_constructor_accepts_every_field():
    @AllArgsConstructor
    class User:
        name: str
        age: int = 0

    user = User("Ada", age=30)
    assert user.name == "Ada"
    assert user.age == 30


def test_all_args_constructor_does_not_generate_repr_eq_or_accessors():
    @AllArgsConstructor
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert not hasattr(point, "get_x")
    assert repr(point) != "Point(x=1, y=2)"


def test_all_args_constructor_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        AllArgsConstructor("not a class")


def test_all_args_constructor_options_is_empty_and_equatable():
    assert AllArgsConstructorOptions() == AllArgsConstructorOptions()
