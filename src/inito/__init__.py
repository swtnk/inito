"""Inito: a Lombok-inspired boilerplate-elimination library for Python."""

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
from inito.decorators.inject import Inject, inject
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
from inito.decorators.resource import Resource, ResourceOptions, resource
from inito.decorators.service import Component, Service, ServiceOptions, component, service
from inito.decorators.setter import Setter, SetterOptions, setter
from inito.decorators.singleton import Singleton, singleton
from inito.decorators.to_string import ToString, ToStringOptions, to_string
from inito.decorators.value import Value, ValueOptions, value
from inito.di.container import Container, Scope, default_container
from inito.di.dependency_resolver import Qualifier
from inito.di.factory import Factory
from inito.di.integrations.fastapi import Injected
from inito.exceptions.errors import InitoError

__version__ = "1.0.0-rc8"

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
