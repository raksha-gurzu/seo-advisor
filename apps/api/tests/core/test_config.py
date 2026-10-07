import pytest
from pydantic import SecretStr

from seo_advisor.core.config import SettingsError, load_settings

VALID_ENV = {
    "APP_ENV": "test",
    "LOG_LEVEL": "info",
    "DATABASE_URL": "postgresql+psycopg://user:s3cret-pass@localhost:5432/db",
}


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Start each test from a known environment. mise loads .env into the shell."""
    for key, value in VALID_ENV.items():
        monkeypatch.setenv(key, value)
    return monkeypatch


@pytest.mark.unit
def test_loads_valid_settings(env: pytest.MonkeyPatch) -> None:
    settings = load_settings()

    assert settings.app_env == "test"
    assert settings.log_level == "info"
    assert isinstance(settings.database_url, SecretStr)
    assert settings.database_url.get_secret_value() == VALID_ENV["DATABASE_URL"]


@pytest.mark.unit
def test_secret_is_hidden_in_text_output(env: pytest.MonkeyPatch) -> None:
    settings = load_settings()

    assert "s3cret-pass" not in str(settings)
    assert "s3cret-pass" not in repr(settings)


@pytest.mark.unit
def test_missing_key_stops_with_clear_message(env: pytest.MonkeyPatch) -> None:
    env.delenv("DATABASE_URL")

    with pytest.raises(SettingsError) as error:
        load_settings()

    message = str(error.value)
    assert "DATABASE_URL (missing)" in message
    assert ".env.example" in message


@pytest.mark.unit
def test_invalid_value_is_named_but_not_repeated(env: pytest.MonkeyPatch) -> None:
    env.setenv("LOG_LEVEL", "loud-value-1234")

    with pytest.raises(SettingsError) as error:
        load_settings()

    message = str(error.value)
    assert "LOG_LEVEL (invalid)" in message
    assert "loud-value-1234" not in message


@pytest.mark.unit
def test_all_problems_are_listed_together(env: pytest.MonkeyPatch) -> None:
    env.delenv("APP_ENV")
    env.delenv("DATABASE_URL")

    with pytest.raises(SettingsError) as error:
        load_settings()

    message = str(error.value)
    assert "APP_ENV (missing)" in message
    assert "DATABASE_URL (missing)" in message
