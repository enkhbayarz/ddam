from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.errors import ServiceUnavailableError
from app.repositories.conversation import ConversationRepository
from app.repositories.persona import PersonaRepository
from app.services.chat import ChatService


@lru_cache  # One shared instance, so every request uses the same lock.
def get_persona_repository() -> PersonaRepository:
    return PersonaRepository(get_settings().personas_path)


@lru_cache
def get_conversation_repository() -> ConversationRepository:
    return ConversationRepository(get_settings().conversations_path)


@lru_cache  # One shared client, so requests reuse its connection pool.
def get_chat_service() -> ChatService:
    settings = get_settings()
    if not settings.ai_gateway_api_key:
        raise ServiceUnavailableError("AI_GATEWAY_API_KEY is not configured")
    client = AsyncOpenAI(
        api_key=settings.ai_gateway_api_key.get_secret_value(),
        base_url=settings.ai_gateway_base_url,
        timeout=60,
    )
    return ChatService(client, settings.ai_gateway_model)


PersonaRepo = Annotated[PersonaRepository, Depends(get_persona_repository)]
ConversationRepo = Annotated[
    ConversationRepository, Depends(get_conversation_repository)
]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
