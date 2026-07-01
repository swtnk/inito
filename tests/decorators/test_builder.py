from dataclasses import dataclass

import pytest

from inito import builder
from inito.decorators.builder import BuilderOptions
from inito.exceptions.errors import BuilderValidationError, DecoratorConfigurationError


def test_bare_builder_generates_fluent_chainable_builder():
    @builder
    class User:
        name: str
        age: int

    user = User.builder().name("Ada").age(30).build()
    assert user.name == "Ada"
    assert user.age == 30


def test_builder_uses_field_defaults_for_unset_optional_fields():
    @builder
    class User:
        name: str
        age: int = 0

    user = User.builder().name("Ada").build()
    assert user.age == 0


def test_builder_raises_when_required_field_left_unset():
    @builder
    class User:
        name: str

    with pytest.raises(BuilderValidationError):
        User.builder().build()


def test_builder_stacked_on_dataclass():
    @builder
    @dataclass
    class Point:
        x: int
        y: int

    point = Point.builder().x(1).y(2).build()
    assert point == Point(1, 2)


def test_builder_to_builder_true_prepopulates_from_instance():
    @builder(to_builder=True)
    @dataclass
    class Point:
        x: int
        y: int

    original = Point(1, 2)
    modified = original.to_builder().y(9).build()
    assert modified.x == 1
    assert modified.y == 9
    assert original == Point(1, 2)


def test_builder_without_to_builder_option_has_no_to_builder_method():
    @builder
    class Point:
        x: int

    assert not hasattr(Point, "to_builder")


def test_builder_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        builder("not a class")


def test_builder_options_defaults():
    assert BuilderOptions() == BuilderOptions(
        to_builder=False, setter_prefix="", build_method_name="build"
    )
