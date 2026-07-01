"""Inito: a Lombok-inspired boilerplate-elimination library for Python."""

from inito.decorators.all_args_constructor import (
    AllArgsConstructor,
    AllArgsConstructorOptions,
    all_args_constructor,
)
from inito.decorators.builder import Builder, BuilderOptions, builder
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
from inito.exceptions.errors import InitoError

__version__ = "0.0.2-beta"

__all__ = [
    "AllArgsConstructor",
    "AllArgsConstructorOptions",
    "Builder",
    "BuilderOptions",
    "Data",
    "DataOptions",
    "EqualsAndHashCode",
    "EqualsAndHashCodeOptions",
    "Getter",
    "GetterOptions",
    "InitoError",
    "NoArgsConstructor",
    "NoArgsConstructorOptions",
    "RequiredArgsConstructor",
    "RequiredArgsConstructorOptions",
    "Setter",
    "SetterOptions",
    "ToString",
    "ToStringOptions",
    "__version__",
    "all_args_constructor",
    "builder",
    "data",
    "equals_and_hash_code",
    "getter",
    "no_args_constructor",
    "required_args_constructor",
    "setter",
    "to_string",
]
