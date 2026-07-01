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


def test_is_class_var_true_for_class_var_annotation():
    assert is_class_var(typing.ClassVar[int]) is True


def test_is_class_var_false_for_plain_type():
    assert is_class_var(int) is False
