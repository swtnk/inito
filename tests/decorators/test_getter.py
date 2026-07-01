import pytest

from inito import Getter
from inito.decorators.getter import GetterOptions
from inito.exceptions.errors import DecoratorConfigurationError


def test_getter_generates_get_methods_for_every_field():
    @Getter
    class User:
        name: str
        age: int = 0

    user = User()
    user.name, user.age = "Ada", 30
    assert user.get_name() == "Ada"
    assert user.get_age() == 30


def test_getter_does_not_generate_constructor_repr_or_setters():
    @Getter
    class Point:
        x: int
        y: int

    point = Point()
    point.x, point.y = 1, 2
    assert point.get_x() == 1
    assert not hasattr(point, "set_x")


def test_getter_with_no_fields_generates_no_methods():
    @Getter
    class Empty:
        pass

    Empty()


def test_getter_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        Getter("not a class")


def test_getter_options_is_empty_and_equatable():
    assert GetterOptions() == GetterOptions()
