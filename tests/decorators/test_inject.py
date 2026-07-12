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


def test_inject_resolves_a_keyword_only_parameter():
    @Service
    class Repo:
        pass

    @Inject
    def handler(*, repo: Repo) -> Repo:
        return repo

    assert isinstance(handler(), Repo)
    sentinel = Repo()
    assert handler(repo=sentinel) is sentinel


def test_inject_injects_a_keyword_only_param_after_var_positional():
    @Service
    class Repo:
        pass

    @Inject
    def handler(*args: int, repo: Repo) -> tuple:
        return args, repo

    args, repo = handler(1, 2, 3)
    assert args == (1, 2, 3)
    assert isinstance(repo, Repo)


def test_inject_does_not_override_a_positionally_supplied_dependency():
    @Service
    class Repo:
        pass

    @Inject
    def handler(repo: Repo) -> Repo:
        return repo

    sentinel = Repo()
    assert handler(sentinel) is sentinel


def test_inject_ignores_unannotated_params_and_var_keyword():
    @Service
    class Repo:
        pass

    @Inject
    def handler(flag, repo: Repo, **extra: object) -> tuple:
        return flag, repo, extra

    flag, repo, extra = handler(True, note="x")
    assert flag is True
    assert isinstance(repo, Repo)
    assert extra == {"note": "x"}


def test_inject_resolves_through_an_active_override():
    container = Container()

    @Service(container=container)
    class Repo:
        pass

    @Inject(container=container)
    def handler(repo: Repo) -> Repo:
        return repo

    # An unrelated override is active: Repo has none, so it resolves normally.
    container.override(str, "unrelated")
    assert isinstance(handler(), Repo)

    # Now override Repo itself: the override wins on the @Inject fast path too.
    stub = Repo()
    container.override(Repo, stub)
    assert handler() is stub
