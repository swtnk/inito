"""Structural edge cases: empty classes, deep inheritance, slots, forward refs."""

from __future__ import annotations

import pytest

from inito import Data, builder
from inito.exceptions.errors import AnnotationResolutionError


def test_empty_class_across_composed_decorators():
    @builder
    @Data
    class Empty:
        pass

    instance = Empty()
    assert repr(instance) == "Empty()"
    assert instance == Empty()
    built = Empty.builder().build()
    assert built == Empty()


def test_single_field_class():
    @Data
    class Wrapper:
        value: int

    wrapper = Wrapper(5)
    assert repr(wrapper) == "Wrapper(value=5)"


def test_three_level_inheritance_chain_accumulates_fields_in_order():
    @Data
    class Level1:
        a: int

    @Data
    class Level2(Level1):
        b: int

    @Data
    class Level3(Level2):
        c: int

    instance = Level3(1, 2, 3)
    assert (instance.a, instance.b, instance.c) == (1, 2, 3)
    assert repr(instance) == "Level3(a=1, b=2, c=3)"


def test_slotted_class_with_required_fields_only():
    @Data
    class Point:
        __slots__ = ("x", "y")
        x: int
        y: int

    point = Point(1, 2)
    assert repr(point) == "Point(x=1, y=2)"


def test_slots_with_class_level_default_conflicts_natively_in_python():
    # Not an inito limitation: Python itself rejects a __slots__ entry that
    # collides with a class-level default, before any decorator ever runs.
    with pytest.raises(ValueError, match="__slots__"):

        class Point:
            __slots__ = ("x",)
            x: int = 0


class _Address:
    pass


def test_forward_reference_to_an_already_defined_class_resolves():
    # _Address must be module-level: get_type_hints resolves string
    # annotations against the class's module globals, not an enclosing
    # function's locals.
    @Data
    class Person:
        name: str
        address: _Address

    person = Person("Ada", _Address())
    assert person.name == "Ada"


def test_self_referential_forward_reference_resolves():
    # inito resolves annotations eagerly, once, at decoration time (the core
    # performance rule) - before the class's own name is bound in module
    # globals. A self-referential annotation (e.g. a linked-list `next: Node`)
    # would naively fail to resolve there, so resolve_type_hints temporarily
    # seeds the module namespace with the class itself before resolving.
    @Data
    class Node:
        value: int
        next: Node | None = None

    n1 = Node(1)
    n2 = Node(2, n1)
    assert n2.next is n1
    assert n2.get_next() is n1


def test_genuinely_unresolvable_annotation_still_fails():
    # The self-reference fix above only seeds the class's own name - a truly
    # undefined name must still fail, not be silently masked.
    with pytest.raises(AnnotationResolutionError):

        @Data
        class Sample:
            value: DoesNotExist  # noqa: F821 -- intentionally unresolvable
