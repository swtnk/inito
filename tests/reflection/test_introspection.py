import sys
import typing

import pytest

from inito.exceptions.errors import AnnotationResolutionError
from inito.reflection.introspection import (
    collect_ordered_field_names,
    is_class_var,
    resolve_type_hints,
)


def test_collect_ordered_field_names_walks_mro_base_first():
    class Base:
        a: int

    class Sub(Base):
        b: int

    assert collect_ordered_field_names(Sub) == ("a", "b")


def test_collect_ordered_field_names_keeps_original_position_on_override():
    class Base:
        a: int
        b: int

    class Sub(Base):
        a: str

    assert collect_ordered_field_names(Sub) == ("a", "b")


def test_resolve_type_hints_resolves_builtin_types():
    class Sample:
        a: int

    assert resolve_type_hints(Sample) == {"a": int}


def test_resolve_type_hints_raises_on_unresolvable_forward_ref():
    class Sample:
        a: "DoesNotExist"  # noqa: F821 -- intentionally unresolvable

    with pytest.raises(AnnotationResolutionError):
        resolve_type_hints(Sample)


def test_resolve_type_hints_resolves_self_referential_annotation():
    class Node:
        value: int
        next: "Node | None" = None

    assert resolve_type_hints(Node)["next"] == typing.Optional[Node]


def test_resolve_type_hints_does_not_leak_the_temporary_self_reference():
    class Node:
        value: int
        next: "Node | None" = None

    resolve_type_hints(Node)
    module = sys.modules[Node.__module__]
    assert not hasattr(module, "Node")


def test_resolve_type_hints_does_not_override_an_existing_module_binding():
    class Sample:
        a: int

    Sample.__name__ = "pytest"  # collide with this module's already-imported `pytest`
    assert resolve_type_hints(Sample) == {"a": int}
    module = sys.modules[Sample.__module__]
    assert module.pytest is pytest  # untouched, not overwritten with Sample


def test_is_class_var_true_for_class_var_annotation():
    assert is_class_var(typing.ClassVar[int]) is True


def test_is_class_var_false_for_plain_type():
    assert is_class_var(int) is False
