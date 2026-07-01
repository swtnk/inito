from dataclasses import dataclass

import pytest

from inito import Data
from inito.decorators.data import DataOptions
from inito.exceptions.errors import DecoratorConfigurationError
from inito.metadata.class_metadata import METADATA_ATTRIBUTE
from inito.metadata.extractor import default_extractor


def test_bare_data_generates_constructor_repr_eq_hash_getters_setters():
    @Data
    class User:
        name: str
        age: int = 0

    user = User("Ada", age=30)
    assert user.name == "Ada"
    assert user.age == 30
    assert repr(user) == "User(name='Ada', age=30)"
    assert user == User("Ada", 30)
    assert hash(user) == hash(User("Ada", 30))
    assert user.get_name() == "Ada"
    user.set_age(31)
    assert user.age == 31


def test_data_frozen_true_omits_setters_but_keeps_getters():
    @Data(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert point.get_x() == 1
    assert not hasattr(point, "set_x")


def test_data_include_getters_false_omits_getters():
    @Data(include_getters=False)
    class Point:
        x: int

    point = Point(1)
    assert not hasattr(point, "get_x")
    point.set_x(5)
    assert point.x == 5


def test_data_include_setters_false_omits_setters():
    @Data(include_setters=False)
    class Point:
        x: int

    point = Point(1)
    assert not hasattr(point, "set_x")
    assert point.get_x() == 1


def test_data_with_inheritance_includes_base_fields():
    @Data
    class Base:
        a: int

    @Data
    class Sub(Base):
        b: int

    instance = Sub(1, 2)
    assert instance.a == 1
    assert instance.b == 2
    assert repr(instance) == "Sub(a=1, b=2)"


def test_data_stacked_on_dataclass():
    @Data(frozen=True)
    @dataclass
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert repr(point) == "Point(x=1, y=2)"
    assert point == Point(1, 2)


def test_data_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        Data("not a class")


def test_data_options_defaults():
    assert DataOptions() == DataOptions(frozen=False, include_getters=True, include_setters=True)


def test_metadata_is_cached_and_not_rebuilt():
    @Data
    class Sample:
        a: int

    cached = Sample.__dict__[METADATA_ATTRIBUTE]
    assert default_extractor.extract(Sample) is cached
