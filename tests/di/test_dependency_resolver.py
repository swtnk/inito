import sys
import typing

import pytest

from inito import RequiredArgsConstructor
from inito.di.dependency_resolver import (
    Dependency,
    registrable_type,
    resolve_constructor_dependencies,
)
from inito.exceptions.errors import DependencyRegistrationError


def test_resolves_simple_constructor_dependencies():
    class A:
        pass

    class B:
        pass

    class Sample:
        def __init__(self, a: A, b: B):
            self.a, self.b = a, b

    assert resolve_constructor_dependencies(Sample) == {
        "a": Dependency(A, False),
        "b": Dependency(B, False),
    }


def test_class_with_no_custom_init_has_no_dependencies():
    class Sample:
        pass

    assert resolve_constructor_dependencies(Sample) == {}


def test_missing_annotation_raises_dependency_registration_error():
    class Sample:
        def __init__(self, value):
            self.value = value

    with pytest.raises(DependencyRegistrationError):
        resolve_constructor_dependencies(Sample)


def test_parameter_with_default_value_is_captured_with_has_default_true():
    class Sample:
        def __init__(self, port: int = 5432):
            self.port = port

    assert resolve_constructor_dependencies(Sample) == {"port": Dependency(int, True)}


def test_self_referential_constructor_annotation_resolves():
    class Node:
        # Optional[Node], not "Node | None": get_type_hints evals this string at
        # runtime, and PEP 604 syntax isn't valid there before Python 3.10.
        def __init__(self, next: "typing.Optional[Node]" = None):
            self.next = next

    dependencies = resolve_constructor_dependencies(Node)
    assert dependencies["next"] == Dependency(typing.Optional[Node], True)


def test_genuinely_unresolvable_annotation_raises_dependency_registration_error():
    class Sample:
        def __init__(self, value: "DoesNotExist"):  # noqa: F821 -- intentionally unresolvable
            self.value = value

    with pytest.raises(DependencyRegistrationError):
        resolve_constructor_dependencies(Sample)


def test_inherited_init_is_resolved_via_mro():
    class Base:
        def __init__(self, a: int):
            self.a = a

    class Sub(Base):
        pass

    assert resolve_constructor_dependencies(Sub) == {"a": Dependency(int, False)}


def test_falls_back_to_cached_field_metadata_for_a_generated_constructor():
    # @RequiredArgsConstructor's generated __init__ source carries no
    # annotations at all - resolve_constructor_dependencies must fall back
    # to the ClassMetadata @RequiredArgsConstructor already cached on the
    # class, rather than requiring a hand-annotated __init__.
    class Repo:
        pass

    @RequiredArgsConstructor
    class Sample:
        repo: Repo

    assert resolve_constructor_dependencies(Sample) == {"repo": Dependency(Repo, False)}


def test_cached_field_metadata_fallback_only_applies_to_missing_annotations():
    # A hand-written, correctly annotated __init__ takes precedence over any
    # cached field metadata (there is none here, since this class was never
    # itself decorated) - this just re-confirms the ordinary path still wins.
    class Repo:
        pass

    class Sample:
        def __init__(self, repo: Repo):
            self.repo = repo

    assert resolve_constructor_dependencies(Sample) == {"repo": Dependency(Repo, False)}


def test_registrable_type_leaves_a_bare_type_unchanged():
    class Sample:
        pass

    assert registrable_type(Sample) is Sample


def test_registrable_type_unwraps_typing_optional():
    class Sample:
        pass

    assert registrable_type(typing.Optional[Sample]) is Sample


@pytest.mark.skipif(sys.version_info < (3, 10), reason="X | Y union syntax needs Python 3.10+")
def test_registrable_type_unwraps_pep604_union_with_none():
    class Sample:
        pass

    assert registrable_type(Sample | None) is Sample


def test_registrable_type_leaves_a_multi_type_union_unchanged():
    class A:
        pass

    class B:
        pass

    union = typing.Union[A, B]
    assert registrable_type(union) == union
