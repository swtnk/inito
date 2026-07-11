from examples.di.settings.app import Report, Settings, container


def test_settings_are_loaded_from_env_and_autowired(monkeypatch):
    monkeypatch.setenv("APP_DATABASE_URL", "postgres://db")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("APP_DEBUG", "true")
    container.reset()  # rebuild the singletons so the new env is read

    report = container.get(Report)
    assert report.settings.database_url == "postgres://db"
    assert report.settings.port == 9000 and isinstance(report.settings.port, int)
    assert report.settings.debug is True


def test_defaults_apply_when_env_absent(monkeypatch):
    for key in ("APP_DATABASE_URL", "APP_PORT", "APP_DEBUG"):
        monkeypatch.delenv(key, raising=False)
    container.reset()

    settings = container.get(Settings)
    assert settings.database_url == "sqlite:///app.db"
    assert settings.port == 8000
    assert settings.debug is False
