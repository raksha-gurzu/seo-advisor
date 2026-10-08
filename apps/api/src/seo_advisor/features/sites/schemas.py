"""Data shapes of the sites feature."""

import uuid
from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

PageType = str


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PageTypeRule(_Frozen):
    """A URL path pattern and its page type. "*" is exactly one whole path part."""

    pattern: str
    page_type: PageType = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")

    @field_validator("pattern")
    @classmethod
    def _check_pattern(cls, pattern: str) -> str:
        if not pattern.startswith("/"):
            raise ValueError("a pattern starts with '/'")
        parts = [p for p in pattern.strip("/").split("/") if p]
        if any("*" in part and part != "*" for part in parts):
            raise ValueError("'*' must be a whole path part, for example /blog/*")
        return pattern


class SiteSpec(_Frozen):
    """One site as written in a site file (infra/sites/*.toml)."""

    tenant: str = Field(min_length=1)
    base_url: str
    language: str = Field(pattern=r"^[a-z]{2}$")
    page_types: list[PageTypeRule]

    @field_validator("base_url")
    @classmethod
    def _check_base_url(cls, base_url: str) -> str:
        parts = urlsplit(base_url)
        if (
            parts.scheme not in ("http", "https")
            or not parts.hostname
            or parts.path not in ("", "/")
            or parts.query
            or parts.fragment
            or parts.username
        ):
            raise ValueError(
                "base_url must be an origin, for example https://site.example"
            )
        return base_url.rstrip("/")


class SiteRecord(_Frozen):
    """A stored site."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    tenant_name: str
    base_url: str
    language: str
    page_types: list[PageTypeRule]
    created_at: datetime
    updated_at: datetime
