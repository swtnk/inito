"""Public decorators.

The DI decorators (``@Service``/``@Component``/``@Singleton``/``@Inject``) are
imported lazily so pulling a data-codegen decorator from this package does not
drag in the dependency-injection layer. See ``inito.__init__`` for the rationale.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from inito.decorators.all_args_constructor import (
    AllArgsConstructor,
    AllArgsConstructorOptions,
    all_args_constructor,
)
from inito.decorators.builder import Builder, BuilderOptions, builder
from inito.decorators.config import Config, ConfigOptions, config
from inito.decorators.data import Data, DataOptions, data
from inito.decorators.equals_and_hash_code import (
    EqualsAndHashCode,
    EqualsAndHashCodeOptions,
    equals_and_hash_code,
)
from inito.decorators.getter import Getter, GetterOptions, getter
from inito.decorators.no_args_constructor import (
    NoArgsConstructor,
    NoArgsConstructorOptions,
    no_args_constructor,
)
from inito.decorators.required_args_constructor import (
    RequiredArgsConstructor,
    RequiredArgsConstructorOptions,
    required_args_constructor,
)
from inito.decorators.setter import Setter, SetterOptions, setter
from inito.decorators.to_string import ToString, ToStringOptions, to_string
from inito.decorators.value import Value, ValueOptions, value

_LAZY_ATTRS = {
    "Component": "inito.decorators.service",
    "Service": "inito.decorators.service",
    "ServiceOptions": "inito.decorators.service",
    "component": "inito.decorators.service",
    "service": "inito.decorators.service",
    "Singleton": "inito.decorators.singleton",
    "singleton": "inito.decorators.singleton",
    "Inject": "inito.decorators.inject",
    "inject": "inito.decorators.inject",
}


def __getattr__(name: str) -> Any:  # noqa: ANN401 -- module-level lazy attribute access (PEP 562)
    module_name = _LAZY_ATTRS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(module_name), name)
    globals()[name] = value
    return value


if TYPE_CHECKING:
    from inito.decorators.inject import Inject, inject
    from inito.decorators.service import (
        Component,
        Service,
        ServiceOptions,
        component,
        service,
    )
    from inito.decorators.singleton import Singleton, singleton

__all__ = [
    "AllArgsConstructor",
    "AllArgsConstructorOptions",
    "Builder",
    "BuilderOptions",
    "Component",
    "Config",
    "ConfigOptions",
    "Data",
    "DataOptions",
    "EqualsAndHashCode",
    "EqualsAndHashCodeOptions",
    "Getter",
    "GetterOptions",
    "Inject",
    "NoArgsConstructor",
    "NoArgsConstructorOptions",
    "RequiredArgsConstructor",
    "RequiredArgsConstructorOptions",
    "Service",
    "ServiceOptions",
    "Setter",
    "SetterOptions",
    "Singleton",
    "ToString",
    "ToStringOptions",
    "Value",
    "ValueOptions",
    "all_args_constructor",
    "builder",
    "component",
    "config",
    "data",
    "equals_and_hash_code",
    "getter",
    "inject",
    "no_args_constructor",
    "required_args_constructor",
    "service",
    "setter",
    "singleton",
    "to_string",
    "value",
]
