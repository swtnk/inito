"""Built-in method generators, registered under stable capability names.

A new decorator is added by implementing a new generator and registering it
here under a new capability name — existing generators are never modified.
"""

from inito.generators.accessors import GetterGenerator, SetterGenerator
from inito.generators.constructor import ConstructorGenerator
from inito.generators.equality import EqGenerator, HashGenerator
from inito.generators.registry import GeneratorRegistry, default_registry
from inito.generators.repr_ import ReprGenerator

default_registry.register("constructor", ConstructorGenerator())
default_registry.register("repr", ReprGenerator())
default_registry.register("eq", EqGenerator())
default_registry.register("hash", HashGenerator())
default_registry.register("getter", GetterGenerator())
default_registry.register("setter", SetterGenerator())

__all__ = ["GeneratorRegistry", "default_registry"]
