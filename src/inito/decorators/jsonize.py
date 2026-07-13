"""@Jsonize: generates to_dict()/to_json() serializing every declared field."""

from __future__ import annotations

from dataclasses import dataclass

from inito.core.attach import attach_capability
from inito.metadata.extractor import default_extractor
from inito.utils.decorator_factory import make_decorator


@dataclass(frozen=True)
class JsonizeOptions:
    """Configuration surface for the @Jsonize decorator (no options yet)."""


def _apply_jsonize(cls: type, options: JsonizeOptions) -> type:
    metadata = default_extractor.extract(cls)
    attach_capability(cls, metadata, "json")
    return cls


Jsonize = make_decorator(_apply_jsonize, JsonizeOptions())
Jsonize.__doc__ = (
    "Generate to_dict() (a JSON-native dict) and to_json() (a JSON string) over "
    "every declared field, coercing datetime/date/time (ISO 8601), UUID, Decimal, "
    "Enum, bytes (base64), Path, mappings, sequences/sets, and nested @Jsonize "
    "objects. to_json forwards its keyword arguments to json.dumps."
)
jsonize = Jsonize

__all__ = ["Jsonize", "JsonizeOptions", "jsonize"]
