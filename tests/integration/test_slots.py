"""The ``slots=True`` option, which recreates the class with ``__slots__``."""

import weakref

import pytest

from inito import Data, Value


def test_data_slots_removes_instance_dict_and_still_constructs():
    @Data(slots=True)
    class Point:
        x: int
        y: int = 0

    point = Point(1, 2)
    assert (point.x, point.y) == (1, 2)
    assert repr(point) == "Point(x=1, y=2)"
    assert not hasattr(point, "__dict__")
    assert "__weakref__" in Point.__slots__


def test_data_slots_rejects_an_undeclared_attribute():
    @Data(slots=True)
    class Point:
        x: int

    with pytest.raises(AttributeError):
        Point(1).z = 5


def test_data_slots_keeps_defaults_getters_and_setters():
    @Data(slots=True)
    class User:
        name: str
        age: int = 0

    user = User("Ada")
    assert user.age == 0
    assert user.get_name() == "Ada"
    user.set_age(31)
    assert user.age == 31


def test_value_slots_is_immutable_hashable_and_slotted():
    @Value(slots=True)
    class UserId:
        value: str

    uid = UserId("abc")
    assert not hasattr(uid, "__dict__")
    assert hash(uid) == hash(UserId("abc"))
    with pytest.raises(Exception):  # noqa: B017 -- FrozenInstanceError
        uid.value = "x"


def test_slots_class_supports_weakref():
    @Data(slots=True)
    class Node:
        n: int

    node = Node(1)
    assert weakref.ref(node)() is node


def test_slots_preserves_super_calls_in_user_methods():
    class Base:
        def label(self) -> str:
            return "base"

    @Data(slots=True)
    class Sub(Base):
        x: int

        def label(self) -> str:
            return "sub-" + super().label()

    assert Sub(1).label() == "sub-base"


def test_slots_runs_post_init():
    @Data(slots=True)
    class Positive:
        value: int

        def __post_init__(self) -> None:
            if self.value < 0:
                raise ValueError("must be >= 0")

    assert Positive(3).value == 3
    with pytest.raises(ValueError, match="must be >= 0"):
        Positive(-1)


def test_slots_leaves_unrelated_closure_cells_untouched():
    secret = "kept"

    @Data(slots=True)
    class Holder:
        x: int

        def reveal(self) -> str:
            return secret  # closes over `secret`, not the class

    assert Holder(1).reveal() == "kept"


def test_slots_default_is_off():
    @Data
    class Plain:
        x: int

    assert hasattr(Plain(1), "__dict__")
