"""Generates a fluent Builder class and the builder()/to_builder() glue for a class.

Builder is structurally different from every other generator: it produces a
whole auxiliary class plus two owner-class methods, not a single method or a
fixed set of per-field methods, and its output depends on per-decoration
options (setter_prefix, build_method_name, to_builder) rather than only on
ClassMetadata. It therefore lives under builders/, not generators/, and is
not registered in the shared GeneratorRegistry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from inito.exceptions.errors import BuilderValidationError
from inito.metadata.class_metadata import ClassMetadata
from inito.metadata.field import FieldMetadata
from inito.utils.codegen import build_function

_UNSET = object()


@dataclass(frozen=True)
class BuilderOptions:
    """Configuration surface for the @Builder decorator."""

    to_builder: bool = False
    setter_prefix: str = ""
    build_method_name: str = "build"
    use_init: bool = False


class BuilderGenerator:
    """Builds the nested Builder class and owner-class glue for @Builder."""

    def build_builder_class(self, metadata: ClassMetadata, options: BuilderOptions) -> type:
        """Return a fresh Builder class with fluent setters and a build method."""
        fields = metadata.fields
        namespace: dict[str, Any] = {
            "__init__": build_function(
                "__init__",
                _render_init_source(fields),
                _init_globals(fields),
                f"{metadata.qualified_name}.Builder.__init__",
            )
        }
        for field in fields:
            method_name = f"{options.setter_prefix}{field.name}"
            namespace[method_name] = build_function(
                method_name,
                _render_fluent_setter_source(field, method_name),
                {},
                f"{metadata.qualified_name}.Builder.{method_name}",
            )
        namespace[options.build_method_name] = build_function(
            options.build_method_name,
            _render_build_method_source(fields, options.build_method_name, options.use_init),
            _build_method_globals(metadata),
            f"{metadata.qualified_name}.Builder.{options.build_method_name}",
        )
        builder_class = type("Builder", (), namespace)
        builder_class.__qualname__ = f"{metadata.qualified_name}.Builder"
        return builder_class

    def build_factory(self, metadata: ClassMetadata) -> Callable[[type], Any]:
        """Return the builder() function attached as a classmethod on the owner class."""
        return build_function(
            "builder",
            "def builder(cls):\n    return cls.Builder()\n",
            {},
            f"{metadata.qualified_name}.builder",
        )

    def build_to_builder(self, metadata: ClassMetadata) -> Callable[[Any], Any]:
        """Return the to_builder() instance method pre-populating a Builder from self."""
        return build_function(
            "to_builder",
            _render_to_builder_source(metadata.fields),
            {},
            f"{metadata.qualified_name}.to_builder",
        )


def _render_init_source(fields: tuple[FieldMetadata, ...]) -> str:
    if not fields:
        return "def __init__(self):\n    pass\n"
    lines = (f"    self._{field.name} = {_initial_value_reference(field)}" for field in fields)
    return "def __init__(self):\n" + "\n".join(lines) + "\n"


def _initial_value_reference(field: FieldMetadata) -> str:
    if field.default_factory is not None:
        return f"_factory_{field.name}()"
    if field.has_default:
        return f"_default_{field.name}"
    return "_unset"


def _init_globals(fields: tuple[FieldMetadata, ...]) -> dict[str, Any]:
    globals_ns: dict[str, Any] = {"_unset": _UNSET}
    for field in fields:
        if field.default_factory is not None:
            globals_ns[f"_factory_{field.name}"] = field.default_factory
        elif field.has_default:
            globals_ns[f"_default_{field.name}"] = field.default
    return globals_ns


def _render_fluent_setter_source(field: FieldMetadata, method_name: str) -> str:
    return f"def {method_name}(self, value):\n    self._{field.name} = value\n    return self\n"


def _render_build_method_source(
    fields: tuple[FieldMetadata, ...], build_method_name: str, use_init: bool
) -> str:
    if use_init:
        return _render_use_init_build_source(fields, build_method_name)
    # Default: build() constructs via __new__ + object.__setattr__ (bound once
    # as _setattr), bypassing __init__. This must stay correct when immutability
    # is applied *after* the builder is generated (e.g. @Value @Builder), which
    # can't be detected here. object.__setattr__ keeps the instance's
    # key-sharing dict intact, so attribute reads stay fast.
    lines = [_render_unset_check(field, build_method_name) for field in fields if field.is_required]
    lines.append("    _instance = _owner_cls.__new__(_owner_cls)")
    lines.extend(f'    _setattr(_instance, "{field.name}", self._{field.name})' for field in fields)
    lines.append("    return _instance")
    return f"def {build_method_name}(self):\n" + "\n".join(lines) + "\n"


def _render_use_init_build_source(fields: tuple[FieldMetadata, ...], build_method_name: str) -> str:
    # use_init=True: construct through the class's own __init__ so a framework
    # (Pydantic/SQLAlchemy/Django) or hand-written constructor runs its
    # validation/instrumentation. The builder becomes a kwargs accumulator:
    # only fields the caller actually set (not left at _unset) are passed, so
    # the target constructor's own defaults and required-argument errors apply
    # rather than inito's. No _unset "required field" check is emitted here -
    # completeness is delegated entirely to __init__.
    lines = ["    _kwargs = {}"]
    for field in fields:
        lines.append(f"    if self._{field.name} is not _unset:")
        lines.append(f'        _kwargs["{field.name}"] = self._{field.name}')
    lines.append("    return _owner_cls(**_kwargs)")
    return f"def {build_method_name}(self):\n" + "\n".join(lines) + "\n"


def _render_unset_check(field: FieldMetadata, build_method_name: str) -> str:
    message = f"{field.name!r} must be set before calling {build_method_name}()."
    return (
        f"    if self._{field.name} is _unset:\n        raise _BuilderValidationError({message!r})"
    )


def _build_method_globals(metadata: ClassMetadata) -> dict[str, Any]:
    return {
        "_unset": _UNSET,
        "_BuilderValidationError": BuilderValidationError,
        "_owner_cls": metadata.owner,
        "_setattr": object.__setattr__,
    }


def _render_to_builder_source(fields: tuple[FieldMetadata, ...]) -> str:
    lines = [f"    _builder._{field.name} = self.{field.name}" for field in fields]
    body = "\n".join(lines) if lines else "    pass"
    header = "def to_builder(self):\n    _builder = self.__class__.Builder()"
    return f"{header}\n{body}\n    return _builder\n"
