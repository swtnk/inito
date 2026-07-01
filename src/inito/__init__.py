"""Inito: a Lombok-inspired boilerplate-elimination library for Python."""

from inito.decorators.all_args_constructor import (
    AllArgsConstructor,
    AllArgsConstructorOptions,
    all_args_constructor,
)
from inito.decorators.data import Data, DataOptions, data
from inito.decorators.getter import Getter, GetterOptions, getter
from inito.decorators.no_args_constructor import (
    NoArgsConstructor,
    NoArgsConstructorOptions,
    no_args_constructor,
)
from inito.decorators.setter import Setter, SetterOptions, setter
from inito.exceptions.errors import InitoError

__version__ = "0.1.0"

__all__ = [
    "AllArgsConstructor",
    "AllArgsConstructorOptions",
    "Data",
    "DataOptions",
    "Getter",
    "GetterOptions",
    "InitoError",
    "NoArgsConstructor",
    "NoArgsConstructorOptions",
    "Setter",
    "SetterOptions",
    "__version__",
    "all_args_constructor",
    "data",
    "getter",
    "no_args_constructor",
    "setter",
]
