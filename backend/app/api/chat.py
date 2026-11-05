from uuid import uuid4

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from app.api.deps import ChatServiceDep, ConversationRepo, PersonaRepo
from app.schemas.chat import ChatMessage, ChatRequest, MessagePart
from app.services.chat import to_ui_message_stream

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(
    body: ChatRequest,
    personas: PersonaRepo,
    conversations: ConversationRepo,
    service: ChatServiceDep,
) -> StreamingResponse:
    # `async def` because this mostly waits on the network. The blocking calls,
    # which touch JSON files, move to a thread to keep the event loop free.
    persona = await run_in_threadpool(personas.get, body.persona_id)

    # Saved before calling the model, so the message survives if the model fails.
    await run_in_threadpool(
        conversations.save_messages, body.id, persona.id, body.messages
    )
    stream = await service.open_stream(persona, body.messages)

    reply = ChatMessage(
        id=uuid4().hex,
        role="assistant",
        parts=[MessagePart(type="text")],
    )
    return StreamingResponse(
        to_ui_message_stream(stream, reply),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "x-vercel-ai-ui-message-stream": "v1",
        },
        # Runs after the stream ends, when the full reply is known.
        background=BackgroundTask(conversations.add_reply, body.id, reply),
    )
