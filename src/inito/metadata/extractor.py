"""Builds and caches ClassMetadata for a class exactly once, at decoration time."""

from __future__ import annotations

import dataclasses
import keyword
import typing

from inito.exceptions.errors import InvalidFieldDefinitionError
from inito.metadata.class_metadata import METADATA_ATTRIBUTE, ClassMetadata
from inito.metadata.field import MISSING, RESERVED_FIELD_PREFIX, FieldMetadata, FieldSpec
from inito.reflection.introspection import (
    collect_ordered_field_names,
    is_class_var,
    is_pydantic_model,
    resolve_type_hints,
)


class MetadataExtractor:
    """Builds and caches ClassMetadata for a class exactly once."""

    def extract(self, cls: type) -> ClassMetadata:
        """Return the cached ClassMetadata for cls, building it if absent."""
        cached = cls.__dict__.get(METADATA_ATTRIBUTE)
        if cached is not None:
            return typing.cast(ClassMetadata, cached)

        fields = self._extract_fields(cls)
        for field in fields:
            _validate_field_name(field.name, cls.__qualname__)
        metadata = ClassMetadata(owner=cls, fields=fields, qualified_name=cls.__qualname__)
        setattr(cls, METADATA_ATTRIBUTE, metadata)
        return metadata

    def _extract_fields(self, cls: type) -> tuple[FieldMetadata, ...]:
        if is_pydantic_model(cls):
            return self._fields_from_pydantic(cls)
        if dataclasses.is_dataclass(cls):
            return self._fields_from_dataclass(cls)
        return self._fields_from_annotations(cls)

    def _fields_from_pydantic(self, cls: type) -> tuple[FieldMetadata, ...]:
        """Read fields from a Pydantic v2 model's ``model_fields``.

        Pydantic keeps a field's default in its ``FieldInfo`` (in
        ``model_fields``), not as a class attribute, so the annotation path's
        ``getattr(cls, name, MISSING)`` would miss it and treat every defaulted
        field as required. Every attribute here is duck-typed - inito never
        imports Pydantic.
        """
        model_fields: dict[str, typing.Any] = cls.model_fields  # type: ignore[attr-defined]
        fields = []
        for name, info in model_fields.items():
            if info.default_factory is not None:
                default, default_factory = MISSING, info.default_factory
            elif not info.is_required():
                default, default_factory = info.default, None
            else:
                default, default_factory = MISSING, None
            fields.append(
                FieldMetadata(
                    name=name,
                    type_hint=info.annotation,
                    default=default,
                    default_factory=default_factory,
                )
            )
        return tuple(fields)

    def _fields_from_dataclass(self, cls: type) -> tuple[FieldMetadata, ...]:
        hints = resolve_type_hints(cls)
        fields = []
        for field in dataclasses.fields(cls):
            default = field.default if field.default is not dataclasses.MISSING else MISSING
            default_factory = (
                field.default_factory if field.default_factory is not dataclasses.MISSING else None
            )
            fields.append(
                FieldMetadata(
                    name=field.name,
                    type_hint=hints[field.name],
                    default=default,
                    default_factory=default_factory,
                )
            )
        return tuple(fields)

    def _fields_from_annotations(self, cls: type) -> tuple[FieldMetadata, ...]:
        ordered_names = collect_ordered_field_names(cls)
        hints = resolve_type_hints(cls)
        fields = []
        for name in ordered_names:
            type_hint = hints[name]
            if is_class_var(type_hint):
                continue
            fields.append(self._field_from_annotation(cls, name, type_hint))
        return tuple(fields)

    def _field_from_annotation(self, cls: type, name: str, type_hint: object) -> FieldMetadata:
        raw = getattr(cls, name, MISSING)
        if isinstance(raw, FieldSpec):
            default, default_factory = raw.default, raw.default_factory
            _normalize_spec_attribute(cls, name, default)
        else:
            default, default_factory = raw, None
        _reject_mutable_default(name, default, cls.__qualname__)
        return FieldMetadata(
            name=name, type_hint=type_hint, default=default, default_factory=default_factory
        )


def _validate_field_name(name: str, qualified_name: str) -> None:
    if not name.isidentifier() or keyword.iskeyword(name):
        raise InvalidFieldDefinitionError(
            f"{qualified_name!r} declares a field named {name!r}, which is not a "
            f"valid Python identifier; inito compiles field names into generated "
            f"method source, so every field must be a plain identifier."
        )
    if name.startswith(RESERVED_FIELD_PREFIX):
        raise InvalidFieldDefinitionError(
            f"{qualified_name!r} declares a field named {name!r}: names starting "
            f"with {RESERVED_FIELD_PREFIX!r} are reserved for inito's generated code."
        )


def _normalize_spec_attribute(cls: type, name: str, default: object) -> None:
    """Replace a ``field(...)`` sentinel left on the class with its plain default.

    Mirrors :func:`dataclasses`: a plain-default spec leaves the value on the
    class (so ``Cls.x`` reads it); a factory-only spec removes the sentinel so a
    class-level read raises ``AttributeError`` rather than returning a FieldSpec.
    Runs at decoration time, before any code generation.
    """
    if default is MISSING:
        if name in cls.__dict__:
            delattr(cls, name)
    else:
        setattr(cls, name, default)


def _reject_mutable_default(name: str, default: object, qualified_name: str) -> None:
    if default is not MISSING and default.__class__.__hash__ is None:
        raise InvalidFieldDefinitionError(
            f"{qualified_name!r} gives field {name!r} a mutable default "
            f"({default.__class__.__name__}); a single instance would be shared "
            f"across every object. Declare it as "
            f"`{name}: ... = field(default_factory=...)` (from inito import field)."
        )


default_extractor = MetadataExtractor()
"""Shared MetadataExtractor instance reused by every decorator."""
