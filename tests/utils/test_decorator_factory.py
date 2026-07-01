from dataclasses import dataclass

import pytest

from inito.exceptions.errors import DecoratorConfigurationError
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class _Options:
    flag: bool = False


def _apply(cls: type, options: _Options) -> type:
    cls.flag = options.flag  # type: ignore[attr-defined]
    return cls


Marker = make_decorator(_apply, _Options())


def test_bare_usage_applies_default_options():
    @Marker
    class Foo:
        pass

    assert Foo.flag is False


def test_call_with_kwargs_overrides_defaults():
    @Marker(flag=True)
    class Foo:
        pass

    assert Foo.flag is True


def test_call_with_options_instance():
    @Marker(_Options(flag=True))
    class Foo:
        pass

    assert Foo.flag is True


def test_call_with_no_args_uses_defaults():
    @Marker()
    class Foo:
        pass

    assert Foo.flag is False


def test_multiple_positional_args_raises():
    with pytest.raises(DecoratorConfigurationError):
        Marker(object(), object())


def test_options_and_kwargs_together_raises():
    with pytest.raises(DecoratorConfigurationError):
        Marker(_Options(), flag=True)


def test_invalid_positional_argument_raises():
    with pytest.raises(DecoratorConfigurationError):
        Marker("not options")
