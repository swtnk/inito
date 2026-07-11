import pytest

from inito.di.container import default_container


@pytest.fixture(autouse=True)
def _reset_default_container():
    """Clear default_container's registrations/singletons before and after each test.

    default_container is process-wide mutable state - the first such state
    in this codebase - so tests that register services must not leak
    registrations into other tests.
    """
    _clear_container_state()
    yield
    _clear_container_state()


def _clear_container_state() -> None:
    default_container._registrations.clear()
    default_container._singletons.clear()
    default_container._overrides.clear()
    default_container._qualified.clear()
    default_container._singleton_locks.clear()
