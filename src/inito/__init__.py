"""Inito: a Lombok-inspired boilerplate-elimination library for Python.

The core - the data-codegen decorators (``@Data``, ``@Value``, ``@Builder``,
accessors, constructors, ``@Config``, ``@Jsonize``, ``field``) - is imported
eagerly. The optional dependency-injection layer (``Container``, ``@Service``,
``@Singleton``, ``@Inject``, ``Factory``, ``@Resource``, FastAPI ``Injected``)
is imported lazily on first access, so ``import inito`` stays DI-free for code
that only wants the data types. Every name is still importable exactly as
before - ``from inito import Container`` triggers the lazy load transparently.
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
from inito.decorators.jsonize import Jsonize, JsonizeOptions, jsonize
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
from inito.exceptions.errors import InitoError
from inito.metadata.field import field

__version__ = "1.0.1"

_LAZY_ATTRS = {
    "Container": "inito.di.container",
    "Scope": "inito.di.container",
    "default_container": "inito.di.container",
    "Qualifier": "inito.di.dependency_resolver",
    "Factory": "inito.di.factory",
    "Injected": "inito.di.integrations.fastapi",
    "Component": "inito.decorators.service",
    "Service": "inito.decorators.service",
    "ServiceOptions": "inito.decorators.service",
    "component": "inito.decorators.service",
    "service": "inito.decorators.service",
    "Singleton": "inito.decorators.singleton",
    "singleton": "inito.decorators.singleton",
    "Inject": "inito.decorators.inject",
    "inject": "inito.decorators.inject",
    "Resource": "inito.decorators.resource",
    "ResourceOptions": "inito.decorators.resource",
    "resource": "inito.decorators.resource",
}
"""The dependency-injection surface: ``name -> module``, imported on first use."""


def __getattr__(name: str) -> Any:  # noqa: ANN401 -- module-level lazy attribute access (PEP 562)
    """Lazily import a DI name on first access, then cache it in the module."""
    module_name = _LAZY_ATTRS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)


if TYPE_CHECKING:
    from inito.decorators.inject import Inject, inject
    from inito.decorators.resource import Resource, ResourceOptions, resource
    from inito.decorators.service import (
        Component,
        Service,
        ServiceOptions,
        component,
        service,
    )
    from inito.decorators.singleton import Singleton, singleton
    from inito.di.container import Container, Scope, default_container
    from inito.di.dependency_resolver import Qualifier
    from inito.di.factory import Factory
    from inito.di.integrations.fastapi import Injected

__all__ = [
    "AllArgsConstructor",
    "AllArgsConstructorOptions",
    "Builder",
    "BuilderOptions",
    "Component",
    "Config",
    "ConfigOptions",
    "Container",
    "Data",
    "DataOptions",
    "EqualsAndHashCode",
    "EqualsAndHashCodeOptions",
    "Factory",
    "Getter",
    "GetterOptions",
    "InitoError",
    "Inject",
    "Injected",
    "Jsonize",
    "JsonizeOptions",
    "NoArgsConstructor",
    "NoArgsConstructorOptions",
    "Qualifier",
    "RequiredArgsConstructor",
    "RequiredArgsConstructorOptions",
    "Resource",
    "ResourceOptions",
    "Scope",
    "Service",
    "ServiceOptions",
    "Setter",
    "SetterOptions",
    "Singleton",
    "ToString",
    "ToStringOptions",
    "Value",
    "ValueOptions",
    "__version__",
    "all_args_constructor",
    "builder",
    "component",
    "config",
    "data",
    "default_container",
    "equals_and_hash_code",
    "field",
    "getter",
    "inject",
    "jsonize",
    "no_args_constructor",
    "required_args_constructor",
    "resource",
    "service",
    "setter",
    "singleton",
    "to_string",
    "value",
]
