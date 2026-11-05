from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.repositories.persona import PersonaRepository
from app.schemas.persona import PersonaCreate

PERSONA = {
    "name": "Ada Lovelace",
    "birthdate": "1815-12-10",
    "lived_place": "London",
    "details": "Mathematician who wrote the first published computer program.",
    "gender": "female",
}


def test_create_list_get_delete(client: TestClient) -> None:
    created = client.post("/api/personas", json=PERSONA)
    assert created.status_code == 201
    body = created.json()
    assert body["success"] is True and body["error"] is None
    persona_id = body["data"]["id"]

    assert [p["id"] for p in client.get("/api/personas").json()["data"]] == [persona_id]
    assert (
        client.get(f"/api/personas/{persona_id}").json()["data"]["name"]
        == "Ada Lovelace"
    )

    assert client.delete(f"/api/personas/{persona_id}").status_code == 204
    assert client.get("/api/personas").json()["data"] == []


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"name": "   "}, "name"),
        ({"gender": "robot"}, "gender"),
        ({"birthdate": "not-a-date"}, "birthdate"),
        ({"birthdate": str(date.today() + timedelta(days=1))}, "birthdate"),
        ({"details": "x" * 2001}, "details"),
    ],
)
def test_invalid_body_returns_422(
    client: TestClient, change: dict[str, str], field: str
) -> None:
    response = client.post("/api/personas", json=PERSONA | change)
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == field


def test_missing_field_returns_422(client: TestClient) -> None:
    body = {k: v for k, v in PERSONA.items() if k != "gender"}
    response = client.post("/api/personas", json=body)
    assert response.status_code == 422
    assert response.json()["error"]["details"][0]["field"] == "gender"


def test_duplicate_name_returns_409(client: TestClient) -> None:
    client.post("/api/personas", json=PERSONA)
    response = client.post("/api/personas", json=PERSONA | {"name": " ada lovelace "})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_unknown_id_returns_404(client: TestClient) -> None:
    for response in (
        client.get(f"/api/personas/{uuid4()}"),
        client.delete(f"/api/personas/{uuid4()}"),
    ):
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"


def test_malformed_id_returns_422(client: TestClient) -> None:
    assert client.get("/api/personas/not-a-uuid").status_code == 422


def test_parallel_creates_keep_every_persona(repo: PersonaRepository) -> None:
    def create(index: int) -> None:
        repo.create(PersonaCreate(**PERSONA | {"name": f"Persona {index}"}))

    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(create, range(50)))

    assert len(repo.list_all()) == 50
