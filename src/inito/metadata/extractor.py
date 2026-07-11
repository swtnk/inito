"""Builds and caches ClassMetadata for a class exactly once, at decoration time."""

from __future__ import annotations

import dataclasses
import typing

from inito.metadata.class_metadata import METADATA_ATTRIBUTE, ClassMetadata
from inito.metadata.field import MISSING, FieldMetadata
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
            fields.append(
                FieldMetadata(
                    name=name,
                    type_hint=type_hint,
                    default=getattr(cls, name, MISSING),
                )
            )
        return tuple(fields)


default_extractor = MetadataExtractor()
"""Shared MetadataExtractor instance reused by every decorator."""
