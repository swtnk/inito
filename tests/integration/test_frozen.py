"""Frozen/immutability behavior: inito's own frozen=True, and interaction with
Python's `@dataclass(frozen=True)`.
"""

from dataclasses import FrozenInstanceError, dataclass

import pytest

from inito import Data, builder


def test_data_frozen_true_is_genuinely_immutable_without_stacking_dataclass():
    @Data(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert point.get_x() == 1
    assert not hasattr(point, "set_x")
    with pytest.raises(FrozenInstanceError):
        point.x = 5
    with pytest.raises(FrozenInstanceError):
        del point.x


def test_data_construction_succeeds_with_dataclass_frozen_innermost():
    # Idiomatic order: @dataclass(frozen=True) is innermost, so its blocking
    # __setattr__ is already on the class when @Data generates its constructor.
    # The constructor detects it (generators/constructor.py::needs_object_setattr)
    # and assigns via object.__setattr__, so construction succeeds and the
    # instance is immutable.
    @Data
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert point == Point(1, 2)
    assert hash(point) == hash(Point(1, 2))
    with pytest.raises(FrozenInstanceError):
        point.x = 5


def test_data_with_dataclass_frozen_outermost_is_unsupported():
    # Non-idiomatic order: @dataclass(frozen=True) is applied *after* @Data has
    # already generated a plain `self.x = x` constructor, which @Data can't
    # predict. Construction then hits the frozen __setattr__ and raises. Use the
    # innermost order above, or @Data(frozen=True)/@Value, for an immutable class.
    @dataclass(frozen=True)
    @Data
    class Point:
        x: int
        y: int

    with pytest.raises(FrozenInstanceError):
        Point(1, 2)


def test_data_setters_and_direct_assignment_still_fail_on_a_frozen_dataclass():
    # Setters remain plain attribute assignment (no object.__setattr__), so
    # post-construction mutation correctly still fails - only construction
    # itself is exempted from the frozen check.
    @Data
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    with pytest.raises(FrozenInstanceError):
        point.set_x(5)
    with pytest.raises(FrozenInstanceError):
        point.x = 5


def test_builder_build_succeeds_on_a_frozen_dataclass():
    @builder
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    point = Point.builder().x(1).y(2).build()
    assert point == Point(1, 2)
    with pytest.raises(FrozenInstanceError):
        point.x = 5
