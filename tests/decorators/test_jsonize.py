"""@Jsonize: generated to_dict()/to_json() over declared fields."""

import datetime
import json
import uuid

from inito import Data, Jsonize, Value


def test_jsonize_to_dict_serializes_declared_fields():
    @Jsonize
    @Data
    class Event:
        id: uuid.UUID
        when: datetime.datetime
        name: str = "x"

    event = Event(
        uuid.UUID("12345678-1234-5678-1234-567812345678"),
        datetime.datetime(2026, 7, 13, 5, 30),
    )
    assert event.to_dict() == {
        "id": "12345678-1234-5678-1234-567812345678",
        "when": "2026-07-13T05:30:00",
        "name": "x",
    }


def test_jsonize_to_json_round_trips_and_forwards_kwargs():
    @Jsonize
    @Value
    class Money:
        amount: int
        currency: str

    money = Money(100, "USD")
    assert json.loads(money.to_json()) == {"amount": 100, "currency": "USD"}
    assert money.to_json(sort_keys=True) == '{"amount": 100, "currency": "USD"}'


def test_jsonize_recurses_into_nested_jsonize_objects():
    @Jsonize
    @Value
    class Inner:
        label: str

    @Jsonize
    @Data
    class Outer:
        inner: Inner

    assert Outer(Inner("deep")).to_dict() == {"inner": {"label": "deep"}}


def test_jsonize_on_a_fieldless_class_yields_an_empty_dict():
    @Jsonize
    class Empty:
        pass

    assert Empty().to_dict() == {}
    assert Empty().to_json() == "{}"


def test_jsonize_lowercase_alias_is_the_same_decorator():
    from inito import jsonize

    assert jsonize is Jsonize
