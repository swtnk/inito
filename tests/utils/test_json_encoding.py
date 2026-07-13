"""serialize_value: coercion of every supported value type to a JSON-native form."""

import datetime
import decimal
import enum
import uuid
from pathlib import PurePosixPath

from inito.utils.json_encoding import serialize_value


class Color(enum.Enum):
    RED = "red"
    LEVEL = 3


def test_none_and_primitives_pass_through():
    assert serialize_value(None) is None
    assert serialize_value("x") == "x"
    assert serialize_value(3) == 3
    assert serialize_value(1.5) == 1.5
    assert serialize_value(True) is True


def test_datetime_date_and_time_use_isoformat():
    assert serialize_value(datetime.date(2026, 7, 13)) == "2026-07-13"
    assert serialize_value(datetime.time(5, 30)) == "05:30:00"
    assert serialize_value(datetime.datetime(2026, 7, 13, 5, 30)) == "2026-07-13T05:30:00"


def test_uuid_and_decimal_become_strings():
    u = uuid.UUID("12345678-1234-5678-1234-567812345678")
    assert serialize_value(u) == str(u)
    assert serialize_value(decimal.Decimal("19.99")) == "19.99"


def test_enum_serializes_its_value_recursively():
    assert serialize_value(Color.RED) == "red"
    assert serialize_value(Color.LEVEL) == 3


def test_bytes_become_base64():
    assert serialize_value(b"hi") == "aGk="
    assert serialize_value(bytearray(b"hi")) == "aGk="


def test_pathlike_becomes_a_string():
    assert serialize_value(PurePosixPath("/a/b")) == "/a/b"


def test_mappings_recurse_with_string_keys():
    assert serialize_value({1: datetime.date(2026, 7, 13)}) == {"1": "2026-07-13"}


def test_sequences_and_sets_become_lists():
    assert serialize_value(("a", 1)) == ["a", 1]
    assert serialize_value([b"hi"]) == ["aGk="]
    assert serialize_value(frozenset({1})) == [1]


def test_objects_with_to_dict_are_recursed():
    class HasToDict:
        def to_dict(self) -> dict:
            return {"when": datetime.date(2026, 7, 13)}

    assert serialize_value(HasToDict()) == {"when": "2026-07-13"}


def test_unknown_types_fall_back_to_str():
    class Opaque:
        def __str__(self) -> str:
            return "opaque"

    assert serialize_value(Opaque()) == "opaque"
