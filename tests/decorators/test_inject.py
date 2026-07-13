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


def test_inject_with_default_resolves_when_registered():
    @Service
    class Repo:
        pass

    @Inject
    def handler(repo: Repo = "fallback") -> object:
        return repo

    assert isinstance(handler(), Repo)


def test_inject_with_default_uses_default_when_unregistered():
    class Unregistered:
        pass

    @Inject
    def handler(value: Unregistered = "the-default") -> object:
        return value

    assert handler() == "the-default"  # unregistered injectable falls back to its own default


def test_inject_preserves_a_passthrough_default_in_the_specialized_wrapper():
    @Service
    class Repo:
        pass

    @Inject
    def handler(repo: Repo, limit=10) -> tuple:  # limit is a passthrough default, not injectable
        return repo, limit

    repo, limit = handler()
    assert isinstance(repo, Repo)
    assert limit == 10


def test_inject_falls_back_when_a_required_param_follows_an_injectable():
    @Service
    class Repo:
        pass

    @Inject
    def handler(repo: Repo, tail) -> tuple:  # required, unannotated positional after an injectable
        return repo, tail

    repo, tail = handler(tail=9)
    assert isinstance(repo, Repo)
    assert tail == 9


def test_inject_generic_path_skips_supplied_and_unregistered():
    @Service
    class Repo:
        pass

    class Unregistered:
        pass

    # ``**extra`` forces the generic wrapper path.
    @Inject
    def handler(repo: Repo, maybe: Unregistered = "d", **extra: object) -> tuple:
        return repo, maybe, extra

    sentinel = Repo()
    repo, maybe, extra = handler(repo=sentinel, note="x")  # repo supplied -> skipped
    assert repo is sentinel  # not overridden
    assert maybe == "d"  # unregistered injectable left to its default
    assert extra == {"note": "x"}


def test_inject_specializes_with_a_leading_required_passthrough_param():
    @Service
    class Repo:
        pass

    @Inject
    def handler(request, repo: Repo) -> tuple:  # required passthrough before the injectable
        return request, repo

    request, repo = handler("req")
    assert request == "req"
    assert isinstance(repo, Repo)


def test_inject_parameter_named_like_a_generated_helper_is_safe():
    @Service
    class Repo:
        pass

    # '_fn' once collided with the generated global holding the wrapped function.
    @Inject
    def handler(_fn, repo: Repo) -> tuple:
        return _fn, repo

    fn_value, repo = handler("caller-value")
    assert fn_value == "caller-value"
    assert isinstance(repo, Repo)


def test_inject_reserved_prefix_parameter_falls_back_to_generic():
    @Service
    class Repo:
        pass

    @Inject
    def handler(_inito_thing, repo: Repo) -> tuple:  # reserved prefix -> generic wrapper
        return _inito_thing, repo

    thing, repo = handler("v")
    assert thing == "v"
    assert isinstance(repo, Repo)
