from typing import Annotated

import pytest

from inito.di.container import Container
from inito.di.dependency_resolver import Qualifier, qualifier_of, registrable_type
from inito.exceptions.errors import AmbiguousDependencyError, UnresolvableDependencyError


class Repo:
    pass


class PostgresRepo(Repo):
    pass


class SqliteRepo(Repo):
    pass


def test_qualifier_marker_selects_the_named_implementation():
    container = Container()
    container.register(PostgresRepo, qualifier="postgres")
    container.register(SqliteRepo, qualifier="sqlite")

    class Service:
        def __init__(self, repo: Annotated[Repo, Qualifier("postgres")]) -> None:
            self.repo = repo

    container.register(Service)
    assert isinstance(container.get(Service).repo, PostgresRepo)


def test_bare_string_qualifier_is_accepted():
    container = Container()
    container.register(SqliteRepo, qualifier="sqlite")

    class Service:
        def __init__(self, repo: Annotated[Repo, "sqlite"]) -> None:
            self.repo = repo

    container.register(Service)
    assert isinstance(container.get(Service).repo, SqliteRepo)


def test_bare_interface_resolves_the_sole_registered_subclass():
    container = Container()
    container.register(PostgresRepo, qualifier="pg")

    class Service:
        def __init__(self, repo: Repo) -> None:
            self.repo = repo

    container.register(Service)
    assert isinstance(container.get(Service).repo, PostgresRepo)


def test_bare_interface_resolves_the_primary_when_several_exist():
    container = Container()
    container.register(PostgresRepo, qualifier="pg", primary=True)
    container.register(SqliteRepo, qualifier="sqlite")

    class Service:
        def __init__(self, repo: Repo) -> None:
            self.repo = repo

    container.register(Service)
    assert isinstance(container.get(Service).repo, PostgresRepo)


def test_ambiguous_bare_interface_without_primary_raises():
    container = Container()
    container.register(PostgresRepo, qualifier="pg")
    container.register(SqliteRepo, qualifier="sqlite")

    class Service:
        def __init__(self, repo: Repo) -> None:
            self.repo = repo

    container.register(Service)
    with pytest.raises(AmbiguousDependencyError, match="multiple registered"):
        container.get(Service)


def test_unknown_qualifier_raises():
    container = Container()

    class Service:
        def __init__(self, repo: Annotated[Repo, "missing"]) -> None:
            self.repo = repo

    container.register(Service)
    with pytest.raises(UnresolvableDependencyError, match="missing"):
        container.get(Service)


def test_duplicate_qualifier_registration_raises():
    from inito.exceptions.errors import DependencyRegistrationError

    container = Container()
    container.register(PostgresRepo, qualifier="db")
    with pytest.raises(DependencyRegistrationError, match="db"):
        container.register(SqliteRepo, qualifier="db")


def test_registrable_type_strips_annotated_and_optional():
    from typing import Optional

    assert registrable_type(Annotated[Repo, "x"]) is Repo
    assert registrable_type(Annotated[Optional[Repo], "x"]) is Repo


def test_qualifier_of_reads_marker_then_string_then_none():
    assert qualifier_of(Annotated[Repo, Qualifier("a")]) == "a"
    assert qualifier_of(Annotated[Repo, "b"]) == "b"
    assert qualifier_of(Repo) is None


def test_qualifier_of_skips_non_matching_metadata():
    assert qualifier_of(Annotated[Repo, 123]) is None
    assert qualifier_of(Annotated[Repo, 123, "pg"]) == "pg"
