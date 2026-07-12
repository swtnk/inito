"""Factory[T]: inject a callable that builds a fresh T per call, autowiring the rest."""

from typing import Annotated

import pytest

from inito.di.container import Container
from inito.di.dependency_resolver import Qualifier
from inito.di.factory import Factory
from inito.exceptions.errors import DependencyRegistrationError


class Repo:
    pass


class Widget:
    """A target built on demand: one autowired dependency, one call-time value."""

    def __init__(self, repo: Repo, title: str) -> None:
        self.repo = repo
        self.title = title


class WidgetMaker:
    """A service that receives a Factory[Widget] and builds widgets on demand."""

    def __init__(self, make_widget: Factory[Widget]) -> None:
        self.make_widget = make_widget


def test_factory_autowires_deps_and_takes_call_time_arg():
    container = Container()
    container.register(Repo)
    container.register(WidgetMaker)
    maker = container.get(WidgetMaker)

    widget = maker.make_widget(title="Sales")

    assert isinstance(widget, Widget)
    assert widget.title == "Sales"
    assert widget.repo is container.get(Repo)  # autowired singleton


def test_call_time_kwarg_overrides_autowiring():
    container = Container()
    container.register(Repo)
    container.register(WidgetMaker)
    maker = container.get(WidgetMaker)

    override_repo = Repo()
    widget = maker.make_widget(title="X", repo=override_repo)

    assert widget.repo is override_repo
    assert widget.repo is not container.get(Repo)


def test_fresh_instance_each_call():
    container = Container()
    container.register(Repo)
    container.register(WidgetMaker)
    maker = container.get(WidgetMaker)

    first = maker.make_widget(title="A")
    second = maker.make_widget(title="A")

    assert first is not second


def test_call_time_only_param_is_required_at_the_call():
    container = Container()
    container.register(Repo)
    container.register(WidgetMaker)
    maker = container.get(WidgetMaker)

    with pytest.raises(TypeError):
        maker.make_widget()  # 'title' has no autowirable type and no default


class OrphanTarget:
    """Not registered anywhere: a Factory builds it as a prototype anyway."""

    def __init__(self, repo: Repo, label: str = "default") -> None:
        self.repo = repo
        self.label = label


class OrphanMaker:
    def __init__(self, make: Factory[OrphanTarget]) -> None:
        self.make = make


def test_unregistered_target_is_built_as_prototype():
    container = Container()
    container.register(Repo)
    container.register(OrphanMaker)
    maker = container.get(OrphanMaker)

    built = maker.make()

    assert isinstance(built, OrphanTarget)
    assert built.repo is container.get(Repo)
    assert built.label == "default"  # falls to the target's own default


class Inner:
    def __init__(self, value: int = 0) -> None:
        self.value = value


class Outer:
    """Its own dependency is itself a factory: nested Factory[...] resolves."""

    def __init__(self, make_inner: Factory[Inner]) -> None:
        self.inner = make_inner(value=7)


class OuterMaker:
    def __init__(self, make_outer: Factory[Outer]) -> None:
        self.make_outer = make_outer


def test_nested_factory_resolves():
    container = Container()
    container.register(OuterMaker)
    maker = container.get(OuterMaker)

    outer = maker.make_outer()

    assert isinstance(outer, Outer)
    assert outer.inner.value == 7


class _CycleServiceA:
    """Would circularly depend on B, but takes a lazy Factory[B] instead."""

    def __init__(self, make_b: "Factory[_CycleServiceB]") -> None:
        self.make_b = make_b


class _CycleServiceB:
    def __init__(self, a: _CycleServiceA) -> None:
        self.a = a


def test_factory_breaks_would_be_cycle():
    container = Container()
    container.register(_CycleServiceA)
    container.register(_CycleServiceB)

    a = container.get(_CycleServiceA)  # no CircularDependencyError: B is built lazily
    b = a.make_b()

    assert isinstance(b, _CycleServiceB)
    assert b.a is a


class Unannotated:
    def __init__(self, mystery) -> None:  # intentionally unannotated
        self.mystery = mystery


class UnannotatedMaker:
    def __init__(self, make: Factory[Unannotated]) -> None:
        self.make = make


def test_unannotated_target_param_raises_when_factory_is_injected():
    # The target's constructor plan is built once, eagerly, when the Factory is
    # injected (fail-fast) - so an unannotated target parameter surfaces while
    # resolving the owning service, not on a later call.
    container = Container()
    container.register(UnannotatedMaker)

    with pytest.raises(DependencyRegistrationError):
        container.get(UnannotatedMaker)


class Postgres(Repo):
    pass


class Sqlite(Repo):
    pass


class QualifiedTarget:
    def __init__(self, repo: Annotated[Repo, Qualifier("pg")], title: str) -> None:
        self.repo = repo
        self.title = title


class QualifiedMaker:
    def __init__(self, make: Factory[QualifiedTarget]) -> None:
        self.make = make


class SecondMaker:
    def __init__(self, make_widget: Factory[Widget]) -> None:
        self.make_widget = make_widget


def test_factory_plan_is_cached_across_targets():
    # Two services request Factory[Widget]; the second _make_factory reuses the
    # cached constructor plan rather than re-resolving it.
    container = Container()
    container.register(Repo)
    container.register(WidgetMaker)
    container.register(SecondMaker)

    first = container.get(WidgetMaker).make_widget(title="a")
    second = container.get(SecondMaker).make_widget(title="b")

    assert first.title == "a"
    assert second.title == "b"


def test_factory_honors_qualifier_on_target_dependency():
    container = Container()
    container.register(Postgres, qualifier="pg")
    container.register(Sqlite, qualifier="lite")
    container.register(QualifiedMaker)
    maker = container.get(QualifiedMaker)

    built = maker.make(title="T")

    assert isinstance(built.repo, Postgres)
