from dataclasses import dataclass

import pytest

from inito import builder
from inito.decorators.builder import BuilderOptions
from inito.exceptions.errors import BuilderValidationError, DecoratorConfigurationError


def test_bare_builder_generates_fluent_chainable_builder():
    @builder
    class User:
        name: str
        age: int

    user = User.builder().name("Ada").age(30).build()
    assert user.name == "Ada"
    assert user.age == 30


def test_builder_uses_field_defaults_for_unset_optional_fields():
    @builder
    class User:
        name: str
        age: int = 0

    user = User.builder().name("Ada").build()
    assert user.age == 0


def test_builder_raises_when_required_field_left_unset():
    @builder
    class User:
        name: str

    with pytest.raises(BuilderValidationError):
        User.builder().build()


def test_builder_stacked_on_dataclass():
    @builder
    @dataclass
    class Point:
        x: int
        y: int

    point = Point.builder().x(1).y(2).build()
    assert point == Point(1, 2)


def test_builder_to_builder_true_prepopulates_from_instance():
    @builder(to_builder=True)
    @dataclass
    class Point:
        x: int
        y: int

    original = Point(1, 2)
    modified = original.to_builder().y(9).build()
    assert modified.x == 1
    assert modified.y == 9
    assert original == Point(1, 2)


def test_builder_without_to_builder_option_has_no_to_builder_method():
    @builder
    class Point:
        x: int

    assert not hasattr(Point, "to_builder")


def test_builder_rejects_non_type_non_options_argument():
    with pytest.raises(DecoratorConfigurationError):
        builder("not a class")


def test_builder_options_defaults():
    assert BuilderOptions() == BuilderOptions(
        to_builder=False, setter_prefix="", build_method_name="build", use_init=False
    )


def test_use_init_builder_constructs_through_the_classs_init():
    calls = []

    @builder(use_init=True)
    class Temperature:
        celsius: float

        def __init__(self, celsius: float) -> None:
            calls.append(celsius)
            self.celsius = round(celsius, 2)

    result = Temperature.builder().celsius(3.14159).build()
    assert result.celsius == 3.14
    assert calls == [3.14159]  # __init__ actually ran


def test_use_init_builder_omits_unset_fields_so_ctor_defaults_apply():
    @builder(use_init=True)
    class Config:
        host: str
        port: int

        def __init__(self, host: str, port: int = 5432) -> None:
            self.host = host
            self.port = port

    config = Config.builder().host("db").build()  # port left unset
    assert (config.host, config.port) == ("db", 5432)


def test_use_init_builder_propagates_ctor_errors():
    @builder(use_init=True)
    class Config:
        host: str
        port: int

        def __init__(self, host: str, port: int) -> None:
            self.host = host
            self.port = port

    # port never set and has no ctor default -> the ctor's own TypeError, not a
    # BuilderValidationError (completeness is delegated to __init__).
    with pytest.raises(TypeError):
        Config.builder().host("db").build()


def test_builder_forces_use_init_on_a_pydantic_target():
    # A Pydantic model (duck-typed here, so no pydantic dependency) makes bare
    # @Builder construct through the model's __init__ instead of the fast
    # bypass, so validation would run. If build() bypassed __init__, `captured`
    # would stay empty.
    captured = {}

    class _FakeFieldInfo:
        annotation = int
        default = 0
        default_factory = None

        def is_required(self) -> bool:
            return False

    def _init(self, **kwargs) -> None:
        captured.update(kwargs)
        self.__dict__.update(kwargs)

    fake_model = type(
        "FakeModel",
        (),
        {
            "model_fields": {"x": _FakeFieldInfo()},
            "__pydantic_validator__": object(),
            "__init__": _init,
        },
    )

    built = builder(fake_model).builder().x(5).build()
    assert captured == {"x": 5}  # constructed via __init__, not the bypass path
    assert built.x == 5


def test_use_init_builder_ignores_inito_visible_class_defaults():
    # In use_init mode the builder must leave even an inito-visible (class-level)
    # default unset, so the target constructor's own default applies rather than
    # inito's. Here the caller doesn't set port, so the ctor default (9999) wins,
    # not the class annotation default (5432).
    @builder(use_init=True)
    class Config:
        host: str
        port: int = 5432

        def __init__(self, host: str, port: int = 9999) -> None:
            self.host = host
            self.port = port

    config = Config.builder().host("db").build()
    assert config.port == 9999


def test_builder_build_populates_a_slotted_class():
    # Slotted classes have no instance __dict__, so build() must fall back to
    # object.__setattr__ rather than a __dict__ write.
    @builder
    class Point:
        __slots__ = ("x", "y")
        x: int
        y: int

    point = Point.builder().x(1).y(2).build()
    assert (point.x, point.y) == (1, 2)
