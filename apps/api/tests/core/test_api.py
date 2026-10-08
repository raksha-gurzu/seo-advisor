import uuid

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from seo_advisor.core.api import NotFoundError, install_api_basics

router = APIRouter()


@router.get("/thing/{thing_id}")
def get_thing(thing_id: uuid.UUID) -> dict[str, str]:
    raise NotFoundError(f"thing {thing_id} does not exist")


@router.get("/boom")
def boom() -> None:
    raise RuntimeError("secret detail that must not leak")


def client() -> TestClient:
    app = FastAPI()
    install_api_basics(app, allowed_hosts=["testserver"])
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.unit
def test_not_found_is_a_problem_document_with_a_request_id() -> None:
    thing = uuid.uuid4()
    response = client().get(f"/thing/{thing}")
    body = response.json()
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert body["title"] == "Not Found"
    assert body["detail"] == f"thing {thing} does not exist"
    assert body["request_id"] == response.headers["x-request-id"]


@pytest.mark.unit
def test_a_validation_error_lists_fields_but_not_the_input() -> None:
    response = client().get("/thing/not-a-uuid")
    body = response.json()
    assert response.status_code == 422
    assert body["errors"][0]["loc"] == ["path", "thing_id"]
    assert "input" not in body["errors"][0]  # pydantic's echo of the value


@pytest.mark.unit
def test_an_unexpected_error_hides_its_message() -> None:
    response = client().get("/boom")
    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert "secret" not in response.text
    assert response.json()["request_id"]


@pytest.mark.unit
def test_a_safe_incoming_request_id_is_kept_and_a_bad_one_is_replaced() -> None:
    kept = client().get("/boom", headers={"X-Request-ID": "abc-123"})
    assert kept.headers["x-request-id"] == "abc-123"
    replaced = client().get("/boom", headers={"X-Request-ID": "bad id\n<script>"})
    assert replaced.headers["x-request-id"] != "bad id\n<script>"
    uuid.UUID(replaced.headers["x-request-id"])


@pytest.mark.unit
def test_a_foreign_host_header_is_refused() -> None:
    # DNS rebinding: a hostile page that points its own name at 127.0.0.1.
    response = client().get("/boom", headers={"Host": "evil.example"})
    assert response.status_code == 400


@pytest.mark.unit
def test_a_wrong_method_keeps_the_allow_header() -> None:
    response = client().post("/boom")
    assert response.status_code == 405
    assert response.headers["allow"] == "GET"
    assert response.headers["content-type"] == "application/problem+json"
