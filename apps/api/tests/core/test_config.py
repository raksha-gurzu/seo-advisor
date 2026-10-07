import pytest
from pydantic import SecretStr

from seo_advisor.core.config import SettingsError, load_settings

VALID_ENV = {
    "APP_ENV": "test",
    "LOG_LEVEL": "info",
    "DATABASE_URL": "postgresql+psycopg://user:s3cret-pass@localhost:5432/db",
    "FETCH_USER_AGENT": "seo-advisor-test/0.1",
    "FETCH_ROBOTS_AGENT": "seo-advisor-test",
    "FETCH_TIMEOUT_S": "20",
    "FETCH_DEADLINE_S": "60",
    "FETCH_MIN_DELAY_S": "1.0",
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


@pytest.mark.unit
def test_fetch_settings_are_loaded(env: pytest.MonkeyPatch) -> None:
    settings = load_settings()

    assert settings.fetch_user_agent == "seo-advisor-test/0.1"
    assert settings.fetch_robots_agent == "seo-advisor-test"
    assert settings.fetch_timeout_s == 20.0
    assert settings.fetch_deadline_s == 60.0
    assert settings.fetch_min_delay_s == 1.0


@pytest.mark.unit
@pytest.mark.parametrize(
    "key", ["FETCH_TIMEOUT_S", "FETCH_DEADLINE_S", "FETCH_MIN_DELAY_S"]
)
def test_fetch_times_must_be_above_zero(env: pytest.MonkeyPatch, key: str) -> None:
    env.setenv(key, "0")

    with pytest.raises(SettingsError, match=f"{key} \\(invalid\\)"):
        load_settings()
