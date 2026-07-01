"""Cross-decorator composition: stacking multiple inito decorators together."""

from dataclasses import dataclass

from inito import (
    AllArgsConstructor,
    Data,
    EqualsAndHashCode,
    Getter,
    Setter,
    ToString,
    builder,
)


def test_data_and_builder_compose_regardless_of_order():
    @Data
    @builder
    class PointA:
        x: int
        y: int

    @builder
    @Data
    class PointB:
        x: int
        y: int

    a = PointA.builder().x(1).y(2).build()
    b = PointB(1, 2)

    assert repr(a) == "PointA(x=1, y=2)"
    assert repr(b) == "PointB(x=1, y=2)"
    assert a.get_x() == 1
    assert b.get_x() == 1


def test_manually_composing_data_equivalent_from_atomic_decorators():
    @AllArgsConstructor
    @ToString
    @EqualsAndHashCode
    @Getter
    @Setter
    class User:
        name: str
        age: int

    user = User("Ada", 30)
    assert repr(user) == "User(name='Ada', age=30)"
    assert user == User("Ada", 30)
    assert hash(user) == hash(User("Ada", 30))
    assert user.get_name() == "Ada"
    user.set_age(31)
    assert user.age == 31


def test_later_applied_decorator_wins_when_capabilities_overlap():
    # Decorators apply bottom-up: @EqualsAndHashCode runs first, then @Data,
    # so @Data's eq/hash ends up attached (it's applied last / outermost).
    @Data
    @EqualsAndHashCode
    class Point:
        x: int
        y: int

    point = Point(1, 2)
    assert repr(point) == "Point(x=1, y=2)"


def test_builder_stacked_on_dataclass_and_to_string():
    @builder
    @ToString
    @dataclass
    class Point:
        x: int
        y: int

    point = Point.builder().x(1).y(2).build()
    assert repr(point) == "Point(x=1, y=2)"
