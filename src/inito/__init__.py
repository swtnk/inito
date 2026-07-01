"""Inito: a Lombok-inspired boilerplate-elimination library for Python."""

from inito.decorators.data import Data, DataOptions, data
from inito.decorators.getter import Getter, GetterOptions, getter
from inito.exceptions.errors import InitoError

__version__ = "0.1.0"

__all__ = [
    "Data",
    "DataOptions",
    "Getter",
    "GetterOptions",
    "InitoError",
    "__version__",
    "data",
    "getter",
]
