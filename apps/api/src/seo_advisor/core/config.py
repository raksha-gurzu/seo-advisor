"""App settings, read once from environment variables.

mise loads `.env` into the environment, so `Settings` reads only the environment.
Every field is required: a missing or invalid value stops start-up.
"""

from typing import Literal

from pydantic import PositiveFloat, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsError(RuntimeError):
    """Settings are missing or invalid. The message never contains values."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True)

    app_env: Literal["local", "test", "ci", "production"]
    log_level: Literal["debug", "info", "warning", "error"]
    database_url: SecretStr

    # Outbound fetch (integrations/http_fetch). Ask the owner before changing the delay.
    fetch_user_agent: str
    fetch_robots_agent: str
    fetch_timeout_s: PositiveFloat
    fetch_deadline_s: PositiveFloat
    fetch_min_delay_s: PositiveFloat


def load_settings() -> Settings:
    """Read and check the settings. Raise SettingsError with a clear message."""
    try:
        return Settings()
    except ValidationError as exc:
        # "from None": the chained ValidationError would print the input values.
        raise SettingsError(_describe(exc)) from None


def _describe(exc: ValidationError) -> str:
    # Use only names and problem kinds. Pydantic's own message repeats the input
    # value, and the value can be a secret.
    problems = []
    for error in exc.errors():
        name = ".".join(str(part) for part in error["loc"]).upper()
        kind = "missing" if error["type"] == "missing" else "invalid"
        problems.append(f"{name} ({kind})")
    return (
        "Settings are missing or invalid: "
        + ", ".join(problems)
        + ". Set them in the environment or in .env (see .env.example)."
    )
