import sys
import typing

import pytest

from inito.exceptions.errors import AnnotationResolutionError, DecoratorConfigurationError
from inito.reflection.introspection import (
    collect_ordered_field_names,
    is_class_var,
    is_pydantic_model,
    reject_pydantic_target,
    resolve_type_hints,
)


def _fake_pydantic_model() -> type:
    # Duck-typed stand-in for a pydantic.BaseModel subclass, so these tests
    # don't depend on pydantic being installed. is_pydantic_model checks these
    # two class-level markers.
    return type("FakeModel", (), {"model_fields": {}, "__pydantic_validator__": object()})


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
        # Optional[Node], not "Node | None": the string is eval'd by
        # get_type_hints at runtime, and PEP 604 syntax isn't valid there
        # before Python 3.10 (this project supports 3.9+).
        next: "typing.Optional[Node]" = None

    assert resolve_type_hints(Node)["next"] == typing.Optional[Node]


def test_resolve_type_hints_does_not_leak_the_temporary_self_reference():
    class Node:
        value: int
        next: "typing.Optional[Node]" = None

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


def test_is_pydantic_model_true_for_duck_typed_model():
    assert is_pydantic_model(_fake_pydantic_model()) is True


def test_is_pydantic_model_false_for_plain_class():
    class Plain:
        pass

    assert is_pydantic_model(Plain) is False


def test_is_pydantic_model_false_without_validator_marker():
    # model_fields alone (e.g. an unrelated class attribute) is not enough.
    partial = type("Partial", (), {"model_fields": {}})
    assert is_pydantic_model(partial) is False


def test_is_pydantic_model_false_when_model_fields_not_a_dict():
    weird = type("Weird", (), {"model_fields": [], "__pydantic_validator__": object()})
    assert is_pydantic_model(weird) is False


def test_reject_pydantic_target_raises_for_model():
    with pytest.raises(DecoratorConfigurationError, match="@Data"):
        reject_pydantic_target(_fake_pydantic_model(), "@Data")


def test_reject_pydantic_target_is_noop_for_plain_class():
    class Plain:
        pass

    reject_pydantic_target(Plain, "@Data")  # must not raise
