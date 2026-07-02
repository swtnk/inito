"""Frozen/immutability behavior: inito's own frozen=True, and interaction with
Python's `@dataclass(frozen=True)`.
"""

from dataclasses import FrozenInstanceError, dataclass

import pytest

from inito import Data, builder


def test_data_frozen_true_produces_a_working_immutable_looking_instance():
    @Data(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert point.get_x() == 1
    assert not hasattr(point, "set_x")


def test_data_construction_succeeds_on_a_frozen_dataclass_in_either_stacking_order():
    # Generated constructors assign fields via object.__setattr__, mirroring
    # how a real frozen dataclass's own __init__ bypasses its blocking
    # __setattr__ for initial construction - so stacking with
    # @dataclass(frozen=True) works regardless of order.
    @Data
    @dataclass(frozen=True)
    class PointA:
        x: int
        y: int

    @dataclass(frozen=True)
    @Data
    class PointB:
        x: int
        y: int

    a = PointA(1, 2)
    b = PointB(1, 2)
    assert a == PointA(1, 2)
    assert hash(a) == hash(PointA(1, 2))
    assert b == PointB(1, 2)
    assert hash(b) == hash(PointB(1, 2))


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
