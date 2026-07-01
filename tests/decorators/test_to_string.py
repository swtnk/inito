import pytest

from inito import ToString
from inito.decorators.to_string import ToStringOptions
from inito.exceptions.errors import DecoratorConfigurationError


def test_to_string_generates_repr_listing_every_field():
    @ToString
    class User:
        name: str
        age: int

    user = User()
    user.name, user.age = "Ada", 30
    assert repr(user) == "User(name='Ada', age=30)"


def test_to_string_does_not_generate_constructor_eq_or_accessors():
    @ToString
    class Point:
        x: int
        y: int

    point = Point()
    assert not hasattr(point, "get_x")
    assert not hasattr(point, "set_x")


def test_to_string_composes_with_builder_for_a_readable_repr():
    from inito import builder

    @builder
    @ToString
    class Point:
        x: int
        y: int

    point = Point.builder().x(1).y(2).build()
    assert repr(point) == "Point(x=1, y=2)"


def test_to_string_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        ToString("not a class")


def test_to_string_options_is_empty_and_equatable():
    assert ToStringOptions() == ToStringOptions()
