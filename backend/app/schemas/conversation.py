from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.chat import ChatMessage


class ConversationSummary(BaseModel):
    id: UUID
    persona_id: UUID
    title: str
    updated_at: datetime


class Conversation(ConversationSummary):
    messages: list[ChatMessage]
