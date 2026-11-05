import json
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from app.repositories.conversation import ConversationRepository
from app.repositories.persona import PersonaRepository
from app.schemas.persona import Persona, PersonaCreate
from tests.test_chat import chunk, sse_response, use_llm, user_message


def make_persona(repo: PersonaRepository, name: str = "Ada") -> Persona:
    return repo.create(
        PersonaCreate(
            name=name,
            birthdate="1815-12-10",
            lived_place="London",
            details="Mathematician.",
            gender="female",
        )
    )


@pytest.fixture
def persona(repo: PersonaRepository) -> Persona:
    return make_persona(repo)


def send(
    client: TestClient, persona_id: UUID, chat_id: UUID, messages: list[dict]
) -> httpx.Response:
    return client.post(
        "/api/chat",
        json={"id": str(chat_id), "persona_id": str(persona_id), "messages": messages},
    )


def reply_with(text: str):
    return lambda _: sse_response(chunk(text) + b"data: [DONE]\n\n")


def test_chat_saves_question_and_reply(client: TestClient, persona: Persona) -> None:
    use_llm(client, reply_with("Hello there"))
    chat_id = uuid4()
    send(client, persona.id, chat_id, [user_message("Hi Ada")])

    saved = client.get(f"/api/conversations/{chat_id}").json()["data"]
    assert saved["title"] == "Hi Ada"
    assert [m["role"] for m in saved["messages"]] == ["user", "assistant"]
    assert saved["messages"][1]["parts"][0]["text"] == "Hello there"


def test_reply_id_matches_the_streamed_id(client: TestClient, persona: Persona) -> None:
    use_llm(client, reply_with("Hello"))
    chat_id = uuid4()
    response = send(client, persona.id, chat_id, [user_message("Hi")])

    streamed = json.loads(response.text.split("\n\n")[0].removeprefix("data: "))
    saved = client.get(f"/api/conversations/{chat_id}").json()["data"]
    assert saved["messages"][1]["id"] == streamed["messageId"]


def test_user_message_is_kept_when_the_model_fails(
    client: TestClient, persona: Persona
) -> None:
    use_llm(client, lambda _: httpx.Response(403, json={"error": {"message": "no"}}))
    chat_id = uuid4()
    assert send(client, persona.id, chat_id, [user_message("Hi")]).status_code == 502

    saved = client.get(f"/api/conversations/{chat_id}").json()["data"]
    assert [m["role"] for m in saved["messages"]] == ["user"]


def test_new_chat_sends_no_old_context(client: TestClient, persona: Persona) -> None:
    sent: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return sse_response(chunk("ok") + b"data: [DONE]\n\n")

    use_llm(client, handler)
    send(client, persona.id, uuid4(), [user_message("My name is Bold")])
    send(client, persona.id, uuid4(), [user_message("What is my name?")])

    assert [m["role"] for m in sent[1]["messages"]] == ["system", "user"]
    assert "Bold" not in json.dumps(sent[1]["messages"])


def test_list_is_newest_first_without_messages(
    client: TestClient, persona: Persona
) -> None:
    use_llm(client, reply_with("ok"))
    first, second = uuid4(), uuid4()
    send(client, persona.id, first, [user_message("First")])
    send(client, persona.id, second, [user_message("Second")])

    items = client.get(f"/api/personas/{persona.id}/conversations").json()["data"]
    assert [item["id"] for item in items] == [str(second), str(first)]
    assert "messages" not in items[0]


def test_list_only_shows_that_persona(
    client: TestClient, repo: PersonaRepository, persona: Persona
) -> None:
    use_llm(client, reply_with("ok"))
    other = make_persona(repo, "Marie")
    send(client, persona.id, uuid4(), [user_message("Hi")])

    assert client.get(f"/api/personas/{other.id}/conversations").json()["data"] == []


def test_long_title_is_shortened_and_stays_after_more_messages(
    client: TestClient, persona: Persona
) -> None:
    use_llm(client, reply_with("ok"))
    chat_id = uuid4()
    first = user_message("x" * 100)
    send(client, persona.id, chat_id, [first])
    send(client, persona.id, chat_id, [first, user_message("Second question")])

    saved = client.get(f"/api/conversations/{chat_id}").json()["data"]
    assert saved["title"] == "x" * 60


def test_chat_id_cannot_move_to_another_persona(
    client: TestClient, repo: PersonaRepository, persona: Persona
) -> None:
    use_llm(client, reply_with("ok"))
    other = make_persona(repo, "Marie")
    chat_id = uuid4()
    send(client, persona.id, chat_id, [user_message("Hi")])

    assert send(client, other.id, chat_id, [user_message("Hi")]).status_code == 409


def test_delete_conversation(client: TestClient, persona: Persona) -> None:
    use_llm(client, reply_with("ok"))
    chat_id = uuid4()
    send(client, persona.id, chat_id, [user_message("Hi")])

    assert client.delete(f"/api/conversations/{chat_id}").status_code == 204
    assert client.get(f"/api/conversations/{chat_id}").status_code == 404
    assert client.delete(f"/api/conversations/{chat_id}").status_code == 404


def test_deleting_a_persona_deletes_its_chats(
    client: TestClient, persona: Persona, conversations: ConversationRepository
) -> None:
    use_llm(client, reply_with("ok"))
    send(client, persona.id, uuid4(), [user_message("Hi")])

    client.delete(f"/api/personas/{persona.id}")

    assert conversations.list_for_persona(persona.id) == []
