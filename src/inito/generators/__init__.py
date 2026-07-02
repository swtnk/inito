"""Built-in method generators, registered under stable capability names.

A new decorator is added by implementing a new generator and registering it
here under a new capability name — existing generators are never modified.
"""

from inito.generators.accessors import GetterGenerator, SetterGenerator
from inito.generators.constructor import (
    ConstructorGenerator,
    NoArgsConstructorGenerator,
    RequiredArgsConstructorGenerator,
)
from inito.generators.equality import EqGenerator, HashGenerator
from inito.generators.immutability import ImmutableGenerator
from inito.generators.registry import GeneratorRegistry, default_registry
from inito.generators.repr_ import ReprGenerator

default_registry.register("constructor", ConstructorGenerator())
default_registry.register("no_args_constructor", NoArgsConstructorGenerator())
default_registry.register("required_args_constructor", RequiredArgsConstructorGenerator())
default_registry.register("repr", ReprGenerator())
default_registry.register("eq", EqGenerator())
default_registry.register("hash", HashGenerator())
default_registry.register("getter", GetterGenerator())
default_registry.register("setter", SetterGenerator())
default_registry.register("immutable", ImmutableGenerator())

__all__ = ["GeneratorRegistry", "default_registry"]
