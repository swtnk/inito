"""Every public decorator must reject non-type/non-options arguments the same way."""

import pytest

from inito import (
    AllArgsConstructor,
    Builder,
    Data,
    EqualsAndHashCode,
    Getter,
    NoArgsConstructor,
    RequiredArgsConstructor,
    Setter,
    ToString,
)
from inito.exceptions.errors import DecoratorConfigurationError

ALL_DECORATORS = [
    Data,
    Getter,
    Setter,
    NoArgsConstructor,
    AllArgsConstructor,
    RequiredArgsConstructor,
    Builder,
    ToString,
    EqualsAndHashCode,
]


@pytest.mark.parametrize("decorator", ALL_DECORATORS)
def test_decorator_rejects_non_type_non_options_argument(decorator):
    with pytest.raises(DecoratorConfigurationError):
        decorator("not a class")


@pytest.mark.parametrize("decorator", ALL_DECORATORS)
def test_decorator_rejects_multiple_positional_arguments(decorator):
    with pytest.raises(DecoratorConfigurationError):
        decorator(object(), object())


@pytest.mark.parametrize("decorator", ALL_DECORATORS)
def test_decorator_bare_and_empty_call_both_apply_defaults(decorator):
    @decorator
    class Bare:
        x: int = 1

    @decorator()
    class Called:
        x: int = 1

    assert type(Bare) is type
    assert type(Called) is type
