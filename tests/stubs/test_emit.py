from typing import Optional

from inito import (
    Builder,
    Data,
    Getter,
    NoArgsConstructor,
    RequiredArgsConstructor,
    Value,
)
from inito.stubs.emit import _builder_class_source, member_stub_source


def test_data_emits_init_accessors_repr_eq_hash():
    @Data
    class User:
        name: str
        age: int = 0

    source = member_stub_source(User)
    assert "def __init__(self, name: str, age: int = ...) -> None: ..." in source
    assert "def get_name(self) -> str: ..." in source
    assert "def set_age(self, value: int) -> None: ..." in source
    assert "def __repr__(self) -> str: ..." in source
    assert "def __eq__(self, other: object) -> bool: ..." in source
    assert "def __hash__(self) -> int: ..." in source


def test_no_args_constructor_emits_zero_argument_init():
    @NoArgsConstructor
    class Config:
        retries: int = 3

    assert "def __init__(self) -> None: ..." in member_stub_source(Config)


def test_required_args_constructor_emits_only_required_params():
    @RequiredArgsConstructor
    class Record:
        a: int
        b: str = "x"

    source = member_stub_source(Record)
    assert "def __init__(self, a: int) -> None: ..." in source
    assert "b:" not in source


def test_getter_emits_only_getters():
    @Getter
    class Box:
        x: int

    source = member_stub_source(Box)
    assert "def get_x(self) -> int: ..." in source
    assert "set_x" not in source


def test_value_emits_getters_and_setattr_guard_but_no_setters():
    @Value
    class Point:
        x: int

    source = member_stub_source(Point)
    assert "def get_x(self) -> int: ..." in source
    assert "set_x" not in source
    assert "def __setattr__(self, name: str, value: object) -> None: ..." in source
    assert "def __delattr__(self, name: str) -> None: ..." in source


def test_builder_emits_nested_builder_factory_and_build():
    @Builder
    class Request:
        path: str
        method: str = "GET"

    source = member_stub_source(Request)
    assert "class Builder:" in source
    assert "def path(self, value: str) -> Request.Builder: ..." in source
    assert "def method(self, value: str) -> Request.Builder: ..." in source
    assert "def build(self) -> Request: ..." in source
    assert "def builder(cls) -> Request.Builder: ..." in source


def test_builder_with_to_builder_emits_it():
    @Builder(to_builder=True)
    class Point:
        x: int
        y: int

    assert "def to_builder(self) -> Point.Builder: ..." in member_stub_source(Point)


def test_optional_field_type_is_rendered():
    @Data
    class Cfg:
        nick: Optional[str] = None

    source = member_stub_source(Cfg)
    # str(Optional[str]) renders as "Optional[str]" up to 3.13 and "str | None"
    # on 3.14+ (PEP 604 repr); both are valid in a .pyi for any type-checker.
    assert "def get_nick(self) -> Optional[str]: ..." in source or (
        "def get_nick(self) -> str | None: ..." in source
    )


def test_class_without_metadata_yields_no_members():
    class Plain:
        pass

    assert member_stub_source(Plain) == ""


def test_builder_source_handles_a_setter_after_the_build_method():
    # A Builder with an arity-0 build(), arity-1 setters, and a method matching
    # neither exercises every branch of the member-classifying loop.
    class FakeBuilder:
        def title(self, value: object) -> object: ...
        def build(self) -> object: ...
        def author(self, value: object) -> object: ...
        def neither(self, a: object, b: object) -> object: ...  # arity 2 -> not a setter/build

    source = _builder_class_source("Book", FakeBuilder, {"title": "str", "author": "str"})

    assert "def title(self, value: str) -> Book.Builder: ..." in source
    assert "def author(self, value: str) -> Book.Builder: ..." in source
    assert "def build(self) -> Book: ..." in source
