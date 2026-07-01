import pytest

from inito import EqualsAndHashCode
from inito.decorators.equals_and_hash_code import EqualsAndHashCodeOptions
from inito.exceptions.errors import DecoratorConfigurationError


@EqualsAndHashCode
class _User:
    name: str
    age: int


def _make(name: str, age: int) -> _User:
    user = _User()
    user.name, user.age = name, age
    return user


def test_equal_instances_compare_equal_and_hash_equal():
    assert _make("Ada", 30) == _make("Ada", 30)
    assert hash(_make("Ada", 30)) == hash(_make("Ada", 30))


def test_unequal_instances_compare_unequal():
    assert _make("Ada", 30) != _make("Ada", 31)


def test_different_class_returns_not_implemented():
    @EqualsAndHashCode
    class Other:
        name: str
        age: int

    other = Other()
    other.name, other.age = "Ada", 30
    assert _make("Ada", 30).__eq__(other) is NotImplemented


def test_equals_and_hash_code_does_not_generate_constructor_repr_or_accessors():
    @EqualsAndHashCode
    class Point:
        x: int
        y: int

    point = Point()
    assert not hasattr(point, "get_x")


def test_equals_and_hash_code_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        EqualsAndHashCode("not a class")


def test_equals_and_hash_code_options_is_empty_and_equatable():
    assert EqualsAndHashCodeOptions() == EqualsAndHashCodeOptions()
