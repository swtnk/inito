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


def test_stacking_data_on_a_frozen_dataclass_raises_frozen_instance_error():
    # inito's generated __init__ does plain `self.x = x`, which correctly
    # respects a frozen dataclass's blocking __setattr__ rather than silently
    # bypassing the immutability the user explicitly asked for. Documented in
    # README as an expected interaction, not a bug to "fix" via
    # object.__setattr__ (that would defeat the frozen guarantee).
    @Data
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    with pytest.raises(FrozenInstanceError):
        Point(1, 2)


def test_stacking_frozen_dataclass_on_data_also_raises_frozen_instance_error():
    @dataclass(frozen=True)
    @Data
    class Point:
        x: int
        y: int

    with pytest.raises(FrozenInstanceError):
        Point(1, 2)


def test_builder_build_also_respects_frozen_dataclass():
    @builder
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    with pytest.raises(FrozenInstanceError):
        Point.builder().x(1).y(2).build()
