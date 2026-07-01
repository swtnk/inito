import pytest

from inito import Setter
from inito.decorators.setter import SetterOptions
from inito.exceptions.errors import DecoratorConfigurationError


def test_setter_generates_set_methods_for_every_field():
    @Setter
    class User:
        name: str
        age: int = 0

    user = User()
    user.set_name("Ada")
    user.set_age(30)
    assert user.name == "Ada"
    assert user.age == 30


def test_setter_does_not_generate_constructor_repr_or_getters():
    @Setter
    class Point:
        x: int
        y: int

    point = Point()
    point.set_x(1)
    assert point.x == 1
    assert not hasattr(point, "get_x")


def test_setter_with_no_fields_generates_no_methods():
    @Setter
    class Empty:
        pass

    Empty()


def test_setter_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        Setter("not a class")


def test_setter_options_is_empty_and_equatable():
    assert SetterOptions() == SetterOptions()
