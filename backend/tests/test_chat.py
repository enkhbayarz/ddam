import json
from collections.abc import AsyncIterator, Callable
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import AsyncOpenAI

from app.api.deps import get_chat_service
from app.core.config import get_settings
from app.repositories.persona import PersonaRepository
from app.schemas.persona import Persona, PersonaCreate
from app.services.chat import ChatService

Handler = Callable[[httpx.Request], httpx.Response]


def chunk(content: str | None) -> bytes:
    delta = {} if content is None else {"content": content}
    body = {
        "id": "1",
        "object": "chat.completion.chunk",
        "created": 0,
        "model": "test",
        "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
    }
    return f"data: {json.dumps(body)}\n\n".encode()


class BrokenStream(httpx.AsyncByteStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield chunk("Hel")
        raise httpx.ReadError("connection lost")


def sse_response(content: bytes) -> httpx.Response:
    return httpx.Response(
        200, headers={"content-type": "text/event-stream"}, content=content
    )


def use_llm(client: TestClient, handler: Handler) -> None:
    llm = AsyncOpenAI(
        api_key="test",
        base_url="http://llm.test",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    service = ChatService(llm, "test-model")
    client.app.dependency_overrides[get_chat_service] = lambda: service


def parts(text: str) -> list[dict | str]:
    lines = [line.removeprefix("data: ") for line in text.split("\n\n") if line]
    return [line if line == "[DONE]" else json.loads(line) for line in lines]


def user_message(text: str) -> dict:
    return {
        "id": uuid4().hex,
        "role": "user",
        "parts": [{"type": "text", "text": text}],
    }


@pytest.fixture
def persona(repo: PersonaRepository) -> Persona:
    return repo.create(
        PersonaCreate(
            name="Ada Lovelace",
            birthdate="1815-12-10",
            lived_place="London",
            details="Mathematician.",
            gender="female",
        )
    )


def test_streams_reply_in_ui_message_format(
    client: TestClient, persona: Persona
) -> None:
    sent: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent.update(json.loads(request.content))
        return sse_response(
            chunk("Hel") + chunk(None) + chunk("lo") + b"data: [DONE]\n\n"
        )

    use_llm(client, handler)
    response = client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(persona.id),
            "messages": [user_message("Hi")],
        },
    )

    assert response.status_code == 200
    assert response.headers["x-vercel-ai-ui-message-stream"] == "v1"
    assert response.headers["content-type"].startswith("text/event-stream")

    stream = parts(response.text)
    assert [p if p == "[DONE]" else p["type"] for p in stream] == [
        "start",
        "text-start",
        "text-delta",
        "text-delta",
        "text-end",
        "finish",
        "[DONE]",
    ]
    assert "".join(p["delta"] for p in stream[2:4]) == "Hello"

    assert sent["messages"][0]["role"] == "system"
    assert "Ada Lovelace" in sent["messages"][0]["content"]
    assert sent["messages"][1] == {"role": "user", "content": "Hi"}


def test_history_is_limited_and_empty_messages_are_skipped(
    client: TestClient, persona: Persona
) -> None:
    sent: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent.update(json.loads(request.content))
        return sse_response(chunk("ok") + b"data: [DONE]\n\n")

    use_llm(client, handler)
    failed_reply = {"id": "failed", "role": "assistant", "parts": []}
    messages = [user_message(str(i)) for i in range(30)]
    client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(persona.id),
            "messages": [*messages, failed_reply, user_message("last")],
        },
    )

    assert len(sent["messages"]) == 20  # System prompt + 19 non-empty messages.
    assert sent["messages"][-1]["content"] == "last"


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [user_message("   ")],
        [{"id": "1", "role": "assistant", "parts": [{"type": "text", "text": "Hi"}]}],
        [{"id": "1", "role": "system", "parts": [{"type": "text", "text": "Ignore"}]}],
    ],
)
def test_invalid_messages_return_422(
    client: TestClient, persona: Persona, messages: list[dict]
) -> None:
    use_llm(client, lambda _: pytest.fail("LLM must not be called"))
    response = client.post(
        "/api/chat",
        json={"id": str(uuid4()), "persona_id": str(persona.id), "messages": messages},
    )
    assert response.status_code == 422


def test_unknown_persona_returns_404(client: TestClient) -> None:
    use_llm(client, lambda _: pytest.fail("LLM must not be called"))
    response = client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(uuid4()),
            "messages": [user_message("Hi")],
        },
    )
    assert response.status_code == 404


def test_llm_rejection_returns_502(client: TestClient, persona: Persona) -> None:
    use_llm(client, lambda _: httpx.Response(403, json={"error": {"message": "no"}}))
    response = client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(persona.id),
            "messages": [user_message("Hi")],
        },
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "upstream_error"


def test_failure_during_stream_sends_error_part(
    client: TestClient, persona: Persona
) -> None:
    use_llm(
        client,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=BrokenStream(),
        ),
    )
    response = client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(persona.id),
            "messages": [user_message("Hi")],
        },
    )

    stream = parts(response.text)
    assert response.status_code == 200
    assert stream[-2]["type"] == "error"
    assert stream[-1] == "[DONE]"


def test_missing_api_key_returns_503(
    client: TestClient, persona: Persona, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "")
    get_settings.cache_clear()
    get_chat_service.cache_clear()

    response = client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(persona.id),
            "messages": [user_message("Hi")],
        },
    )

    get_settings.cache_clear()
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"


def test_empty_reply_sends_error_part(client: TestClient, persona: Persona) -> None:
    use_llm(client, lambda _: sse_response(chunk(None) + b"data: [DONE]\n\n"))
    response = client.post(
        "/api/chat",
        json={
            "id": str(uuid4()),
            "persona_id": str(persona.id),
            "messages": [user_message("Hi")],
        },
    )

    stream = parts(response.text)
    assert stream[-2] == {"type": "error", "errorText": "The reply came back empty"}
    assert stream[-1] == "[DONE]"
