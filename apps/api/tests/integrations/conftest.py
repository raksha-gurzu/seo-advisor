import socket
from typing import Any

import pytest

from seo_advisor.integrations.http_fetch.client import FetchConfig

PUBLIC_IP = "93.184.215.14"


@pytest.fixture
def config() -> FetchConfig:
    return FetchConfig(
        user_agent="seo-advisor-test/0.1",
        robots_agent="seo-advisor-test",
        timeout_s=5.0,
        deadline_s=30.0,
        min_delay_s=1.0,
    )


@pytest.fixture
def dns(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Fake DNS for one test: no test sends a real DNS query. Add host -> addresses."""
    answers: dict[str, list[str]] = {}

    def getaddrinfo(
        host: str, port: int | None, *args: Any, **kwargs: Any
    ) -> list[Any]:
        if host not in answers:
            raise socket.gaierror("no such host")
        return [(0, 0, 0, "", (a, port or 0)) for a in answers[host]]

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    return answers
