"""Generic class support: decorating classes parameterized with TypeVar/Generic."""

from typing import Generic, TypeVar

from inito import Data, builder

T = TypeVar("T")


def test_data_on_a_generic_class():
    @Data
    class Box(Generic[T]):
        value: T

    box = Box(5)
    assert box.value == 5
    assert box.get_value() == 5
    assert repr(box) == "Box(value=5)"
    assert box == Box(5)


def test_builder_on_a_generic_class():
    @builder
    class Box(Generic[T]):
        value: T

    box: Box[str] = Box.builder().value("hello").build()
    assert box.value == "hello"
