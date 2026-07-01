"""Generates get_<field>()/set_<field>(value) accessors for every field."""

from __future__ import annotations

from inito.generators.base import GeneratedMethod
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata
from inito.utils.codegen import build_function


class GetterGenerator:
    """Generates get_<field>() accessor methods for every declared field."""

    def generate_all(self, metadata: ClassMetadata) -> tuple[GeneratedMethod, ...]:
        """Return one get_<field>() method per declared field."""
        return tuple(_build_getter(metadata.qualified_name, field) for field in metadata.fields)


class SetterGenerator:
    """Generates set_<field>(value) mutator methods for every declared field."""

    def generate_all(self, metadata: ClassMetadata) -> tuple[GeneratedMethod, ...]:
        """Return one set_<field>(value) method per declared field."""
        return tuple(_build_setter(metadata.qualified_name, field) for field in metadata.fields)


def _build_getter(qualified_name: str, field: FieldMetadata) -> GeneratedMethod:
    method_name = f"get_{field.name}"
    source = f"def {method_name}(self):\n    return self.{field.name}\n"
    function = build_function(method_name, source, {}, f"{qualified_name}.{method_name}")
    return GeneratedMethod(name=method_name, callable=function)


def _build_setter(qualified_name: str, field: FieldMetadata) -> GeneratedMethod:
    method_name = f"set_{field.name}"
    source = f"def {method_name}(self, value):\n    self.{field.name} = value\n"
    function = build_function(method_name, source, {}, f"{qualified_name}.{method_name}")
    return GeneratedMethod(name=method_name, callable=function)
