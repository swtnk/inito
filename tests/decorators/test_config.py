from typing import Optional

import pytest

from inito import Config
from inito.exceptions import ConfigResolutionError


def test_config_loads_and_coerces_from_env(monkeypatch):
    monkeypatch.setenv("APP_DB_URL", "postgres://x")
    monkeypatch.setenv("APP_PORT", "6543")
    monkeypatch.setenv("APP_DEBUG", "yes")

    @Config(prefix="APP_")
    class Settings:
        db_url: str
        port: int = 5432
        debug: bool = False

    settings = Settings()
    assert settings.db_url == "postgres://x"
    assert settings.port == 6543 and isinstance(settings.port, int)
    assert settings.debug is True


def test_config_uses_defaults_when_env_absent(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)

    @Config
    class Settings:
        port: int = 5432
        nick: Optional[str] = None

    settings = Settings()
    assert settings.port == 5432
    assert settings.nick is None


def test_config_missing_required_field_raises(monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)

    @Config
    class Settings:
        db_url: str

    with pytest.raises(ConfigResolutionError, match="DB_URL"):
        Settings()


def test_config_invalid_coercion_raises(monkeypatch):
    monkeypatch.setenv("PORT", "not-an-int")

    @Config
    class Settings:
        port: int

    with pytest.raises(ConfigResolutionError, match="port"):
        Settings()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", True),
        ("true", True),
        ("YES", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("off", False),
    ],
)
def test_config_bool_parsing(monkeypatch, raw, expected):
    monkeypatch.setenv("FLAG", raw)

    @Config
    class Settings:
        flag: bool

    assert Settings().flag is expected


def test_config_invalid_bool_raises(monkeypatch):
    monkeypatch.setenv("FLAG", "maybe")

    @Config
    class Settings:
        flag: bool

    with pytest.raises(ConfigResolutionError):
        Settings()


def test_config_prefix_is_applied(monkeypatch):
    monkeypatch.setenv("SVC_NAME", "auth")
    monkeypatch.setenv("NAME", "wrong")

    @Config(prefix="SVC_")
    class Settings:
        name: str

    assert Settings().name == "auth"


def test_config_env_overrides_field_default(monkeypatch):
    monkeypatch.setenv("RETRIES", "9")

    @Config
    class Settings:
        retries: int = 3

    assert Settings().retries == 9


def test_config_unsupported_and_union_types_fall_back_to_raw_string(monkeypatch):
    from typing import Union

    monkeypatch.setenv("A", "x")
    monkeypatch.setenv("B", "y")

    @Config
    class Settings:
        a: list  # unsupported scalar -> raw string
        b: Union[int, str]  # ambiguous union -> raw string

    settings = Settings()
    assert settings.a == "x"
    assert settings.b == "y"


def test_config_coerces_float_field(monkeypatch):
    monkeypatch.setenv("RATIO", "0.75")

    @Config
    class Settings:
        ratio: float

    assert Settings().ratio == 0.75
