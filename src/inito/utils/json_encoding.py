"""Coerce field values to JSON-native forms for @Jsonize's generated ``to_dict``.

The field *structure* is fixed at decoration time; only the per-value coercion
here runs at call time, since a field's runtime value type isn't known until then.
"""

from __future__ import annotations

import base64
import collections.abc
import datetime
import decimal
import enum
import os
import uuid
from typing import Any

_PRIMITIVES = (str, int, float, bool)


def serialize_value(value: Any) -> Any:  # noqa: ANN401 -- arbitrary field value in, JSON-native out
    """Return a JSON-native form of value, recursively; unknown types are stringified.

    Handles ``datetime``/``date``/``time`` (ISO 8601), ``UUID``, ``Decimal``,
    ``Enum`` (by value), ``bytes`` (base64), ``os.PathLike``, mappings, sequences
    and sets, and any object exposing a ``to_dict()`` (e.g. a nested ``@Jsonize``).
    """
    if value is None or isinstance(value, _PRIMITIVES):
        return value
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, decimal.Decimal):
        return str(value)
    if isinstance(value, enum.Enum):
        return serialize_value(value.value)
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(value).decode("ascii")
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, collections.abc.Mapping):
        return {str(key): serialize_value(item) for key, item in value.items()}
    if isinstance(value, (collections.abc.Sequence, collections.abc.Set)):
        return [serialize_value(item) for item in value]
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return serialize_value(to_dict())
    return str(value)
