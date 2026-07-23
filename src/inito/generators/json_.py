"""Generates ``to_dict()`` and ``to_json()`` serializing every declared field."""

from __future__ import annotations

import json

from inito.generators.base import GeneratedMethod
from inito.metadata.class_metadata import ClassMetadata
from inito.utils.codegen import build_function
from inito.utils.json_encoding import serialize_value

_TO_JSON_SOURCE = (
    "def to_json(self, **kwargs):\n    return _inito_dumps(self.to_dict(), **kwargs)\n"
)


class JsonGenerator:
    """Generates ``to_dict()`` (a JSON-native dict) and ``to_json()`` (a JSON string)."""

    def generate_all(self, metadata: ClassMetadata) -> tuple[GeneratedMethod, ...]:
        """Return the ``to_dict``/``to_json`` pair for metadata's declared fields."""
        qualname = metadata.qualified_name
        to_dict = build_function(
            "to_dict",
            _to_dict_source(metadata),
            {"_inito_serialize": serialize_value},
            f"{qualname}.to_dict",
        )
        to_json = build_function(
            "to_json", _TO_JSON_SOURCE, {"_inito_dumps": json.dumps}, f"{qualname}.to_json"
        )
        return (
            GeneratedMethod(name="to_dict", callable=to_dict),
            GeneratedMethod(name="to_json", callable=to_json),
        )


def _to_dict_source(metadata: ClassMetadata) -> str:
    if not metadata.fields:
        return "def to_dict(self):\n    return {}\n"
    items = "".join(
        f'        "{field.name}": _inito_serialize(self.{field.name}),\n'
        for field in metadata.fields
    )
    return f"def to_dict(self):\n    return {{\n{items}    }}\n"
