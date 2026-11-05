from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_persona_repository
from app.main import create_app
from app.repositories.persona import PersonaRepository


@pytest.fixture
def repo(tmp_path: Path) -> PersonaRepository:
    return PersonaRepository(tmp_path / "personas.json")


@pytest.fixture
def client(repo: PersonaRepository) -> Iterator[TestClient]:
    app = create_app()
    # Dependency injection pays off here: tests never touch the real data file.
    app.dependency_overrides[get_persona_repository] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client
