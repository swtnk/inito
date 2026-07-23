"""The user ``__post_init__`` hook, run after generated construction."""

import pytest

from inito import (
    AllArgsConstructor,
    Builder,
    Data,
    NoArgsConstructor,
    RequiredArgsConstructor,
    Value,
)


def test_data_runs_post_init_after_assigning_fields():
    calls = []

    @Data
    class Threshold:
        value: float

        def __post_init__(self) -> None:
            calls.append(self.value)

    Threshold(5.0)
    assert calls == [5.0]


def test_post_init_can_enforce_an_invariant():
    @Data
    class Positive:
        value: int

        def __post_init__(self) -> None:
            if self.value < 0:
                raise ValueError("must be >= 0")

    with pytest.raises(ValueError, match="must be >= 0"):
        Positive(-1)


def test_frozen_value_post_init_sets_a_derived_field_via_object_setattr():
    @Value
    class Circle:
        radius: float

        def __post_init__(self) -> None:
            object.__setattr__(self, "area", 3.14 * self.radius**2)

    assert Circle(2.0).area == pytest.approx(12.56)


def test_no_args_and_required_args_constructors_run_post_init():
    seen = []

    @NoArgsConstructor
    class A:
        x: int = 1

        def __post_init__(self) -> None:
            seen.append("A")

    @RequiredArgsConstructor
    class B:
        x: int

        def __post_init__(self) -> None:
            seen.append("B")

    A()
    B(1)
    assert seen == ["A", "B"]


def test_all_args_constructor_runs_post_init():
    seen = []

    @AllArgsConstructor
    class Point:
        x: int
        y: int

        def __post_init__(self) -> None:
            seen.append((self.x, self.y))

    Point(1, 2)
    assert seen == [(1, 2)]


def test_builder_default_build_runs_post_init():
    @Builder
    class Config:
        n: int

        def __post_init__(self) -> None:
            if self.n == 0:
                raise ValueError("n cannot be 0")

    assert Config.builder().n(5).build().n == 5
    with pytest.raises(ValueError, match="n cannot be 0"):
        Config.builder().n(0).build()


def test_builder_use_init_runs_post_init_exactly_once():
    calls = []

    @Builder(use_init=True)
    @Data
    class Config:
        n: int

        def __post_init__(self) -> None:
            calls.append(self.n)

    Config.builder().n(3).build()
    assert calls == [3]


def test_inherited_post_init_is_called():
    calls = []

    class Base:
        def __post_init__(self) -> None:
            calls.append("base")

    @Data
    class Sub(Base):
        x: int

    Sub(1)
    assert calls == ["base"]


def test_no_post_init_hook_constructs_normally():
    @Data
    class Plain:
        x: int

    assert Plain(1).x == 1
