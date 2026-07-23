from dataclasses import FrozenInstanceError, dataclass
from datetime import date

import pytest

from inito import Builder, Value
from inito.decorators.value import ValueOptions
from inito.exceptions.errors import DecoratorConfigurationError


def test_bare_value_generates_constructor_repr_eq_hash_getters_no_setters():
    @Value
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
    assert not hasattr(user, "set_name")
    assert not hasattr(user, "set_age")


def test_value_is_genuinely_immutable_with_no_dataclass_stacking():
    @Value
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    with pytest.raises(FrozenInstanceError):
        point.x = 5
    with pytest.raises(FrozenInstanceError):
        del point.x


def test_value_with_builder_is_immutable_after_build():
    # Regression test for the exact reported scenario: @Value + @Builder,
    # no @dataclass(frozen=True) stacking - direct attribute assignment on
    # the built instance must raise, not silently succeed.
    @Value
    @Builder
    class Person:
        name: str
        dob: date
        address: str

    person = Person.builder().name("Alice").dob(date(1990, 1, 1)).address("123 Main St").build()
    assert person.name == "Alice"
    with pytest.raises(FrozenInstanceError):
        person.name = "Bob"


def test_value_include_getters_false_omits_getters():
    @Value(include_getters=False)
    class Point:
        x: int

    point = Point(1)
    assert point.x == 1
    assert not hasattr(point, "get_x")


def test_value_with_inheritance_includes_base_fields():
    @Value
    class Base:
        a: int

    @Value
    class Sub(Base):
        b: int

    instance = Sub(1, 2)
    assert instance.a == 1
    assert instance.b == 2
    assert repr(instance) == "Sub(a=1, b=2)"


def test_value_stacked_on_frozen_dataclass_enforces_real_immutability():
    @Value
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert repr(point) == "Point(x=1, y=2)"
    assert point == Point(1, 2)
    with pytest.raises(FrozenInstanceError):
        point.x = 5


def test_value_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        Value("not a class")


def test_value_options_defaults():
    assert ValueOptions() == ValueOptions(
        include_getters=True, slots=False, freeze_collections=False
    )


def test_freeze_collections_converts_mutable_values_to_immutable():
    from types import MappingProxyType

    @Value(freeze_collections=True)
    class Bag:
        items: list
        tags: set
        meta: dict

    bag = Bag([1, 2], {3, 4}, {"a": 1})
    assert bag.items == (1, 2)
    assert isinstance(bag.items, tuple)
    assert bag.tags == frozenset({3, 4})
    assert isinstance(bag.meta, MappingProxyType)
    with pytest.raises(TypeError):
        bag.meta["b"] = 2


def test_freeze_collections_makes_a_list_field_hashable():
    @Value(freeze_collections=True)
    class Tags:
        names: list

    assert hash(Tags(["a", "b"])) == hash(Tags(["a", "b"]))


def test_freeze_collections_leaves_non_collection_fields_untouched():
    @Value(freeze_collections=True)
    class Point:
        x: int
        label: str

    point = Point(1, "a")
    assert (point.x, point.label) == (1, "a")


def test_value_without_freeze_collections_keeps_a_list():
    @Value
    class Bag:
        items: list

    assert isinstance(Bag([1]).items, list)
