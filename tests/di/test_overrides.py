from inito.di.container import Container, Scope


class Repo:
    pass


class FakeRepo:
    pass


class Service:
    def __init__(self, repo: Repo) -> None:
        self.repo = repo


def test_override_returns_the_given_instance():
    container = Container()
    container.register(Repo)
    fake = FakeRepo()
    container.override(Repo, fake)

    assert container.get(Repo) is fake


def test_override_wins_over_a_cached_singleton():
    container = Container()
    container.register(Repo)
    real = container.get(Repo)  # caches the singleton

    fake = FakeRepo()
    container.override(Repo, fake)
    assert container.get(Repo) is fake
    assert container.get(Repo) is not real


def test_override_is_injected_into_dependents():
    container = Container()
    container.register(Repo)
    container.register(Service)

    fake = FakeRepo()
    container.override(Repo, fake)
    assert container.get(Service).repo is fake


def test_override_does_not_require_registration():
    container = Container()
    fake = FakeRepo()
    container.override(Repo, fake)  # Repo never registered

    assert container.get(Repo) is fake


def test_override_factory_is_called_each_resolution():
    container = Container()
    container.register(Repo, scope=Scope.TRANSIENT)
    calls = []

    def make() -> FakeRepo:
        instance = FakeRepo()
        calls.append(instance)
        return instance

    container.override_factory(Repo, make)
    first, second = container.get(Repo), container.get(Repo)

    assert first is not second
    assert calls == [first, second]


def test_clear_override_restores_real_resolution():
    container = Container()
    container.register(Repo)
    container.override(Repo, FakeRepo())
    container.clear_override(Repo)

    assert isinstance(container.get(Repo), Repo)


def test_overrides_context_manager_scopes_and_restores():
    container = Container()
    container.register(Repo)
    container.register(Service)

    fake = FakeRepo()
    with container.overrides({Repo: fake}):
        assert container.get(Service).repo is fake

    assert isinstance(container.get(Service).repo, Repo)


def test_overrides_context_manager_restores_prior_overrides():
    container = Container()
    container.register(Repo)
    first = FakeRepo()
    container.override(Repo, first)

    with container.overrides({Repo: FakeRepo()}):
        assert container.get(Repo) is not first
    assert container.get(Repo) is first  # prior override restored, not cleared


def test_reset_clears_overrides():
    container = Container()
    container.register(Repo)
    container.override(Repo, FakeRepo())
    container.reset()

    assert isinstance(container.get(Repo), Repo)


def test_clear_overrides_removes_all():
    container = Container()
    container.register(Repo)
    container.register(Service)
    container.override(Repo, FakeRepo())
    container.clear_overrides()

    assert isinstance(container.get(Repo), Repo)


def test_get_with_no_overrides_is_unaffected():
    container = Container()
    container.register(Repo)
    instance = container.get(Repo)

    assert container.get(Repo) is instance  # warm singleton path still works
    assert not container._overrides


def test_override_factory_value_is_returned_as_is():
    # A factory result is returned verbatim (overrides don't special-case None).
    container = Container()
    sentinel = object()
    container.override_factory(Repo, lambda: sentinel)
    assert container.get(Repo) is sentinel
