from inito import Inject, Service
from inito.di.container import Container


def test_inject_resolves_annotated_params_from_container():
    @Service
    class Repo:
        pass

    @Inject
    def handler(repo: Repo) -> Repo:
        return repo

    assert isinstance(handler(), Repo)


def test_inject_leaves_explicitly_passed_args_untouched():
    @Service
    class Repo:
        pass

    sentinel = Repo()

    @Inject
    def handler(repo: Repo) -> Repo:
        return repo

    assert handler(sentinel) is sentinel
    assert handler(repo=sentinel) is sentinel


def test_inject_with_explicit_container_option():
    custom = Container()

    class Repo:
        pass

    custom.register(Repo)

    @Inject(container=custom)
    def handler(repo: Repo) -> Repo:
        return repo

    assert isinstance(handler(), Repo)


def test_inject_raises_if_dependency_missing_and_unregistered():
    class Repo:
        pass

    @Inject
    def handler(repo: Repo) -> Repo:
        return repo

    try:
        handler()
    except TypeError:
        pass
    else:
        raise AssertionError("expected a TypeError for the missing, unregistered argument")


def test_inject_preserves_function_metadata():
    @Inject
    def handler() -> None:
        """Docstring."""

    assert handler.__name__ == "handler"
    assert handler.__doc__ == "Docstring."


def test_inject_works_with_partial_manual_args_partial_injected():
    @Service
    class Repo:
        pass

    @Inject
    def handler(name: str, repo: Repo) -> tuple:
        return name, repo

    name, repo = handler("Ada")
    assert name == "Ada"
    assert isinstance(repo, Repo)
