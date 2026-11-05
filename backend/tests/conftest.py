from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_conversation_repository, get_persona_repository
from app.main import create_app
from app.repositories.conversation import ConversationRepository
from app.repositories.persona import PersonaRepository


@pytest.fixture
def repo(tmp_path: Path) -> PersonaRepository:
    return PersonaRepository(tmp_path / "personas.json")


@pytest.fixture
def conversations(tmp_path: Path) -> ConversationRepository:
    return ConversationRepository(tmp_path / "conversations.json")


@pytest.fixture
def client(
    repo: PersonaRepository, conversations: ConversationRepository
) -> Iterator[TestClient]:
    app = create_app()
    # Dependency injection pays off here: tests never touch the real data file.
    app.dependency_overrides[get_persona_repository] = lambda: repo
    app.dependency_overrides[get_conversation_repository] = lambda: conversations
    with TestClient(app) as test_client:
        yield test_client
