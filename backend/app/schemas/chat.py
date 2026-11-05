from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class MessagePart(BaseModel):
    type: str
    text: str = Field(default="", max_length=8000)


class ChatMessage(BaseModel):
    """Matches the AI SDK message shape that `useChat` sends.

    `system` is not an allowed role, so a client cannot override the persona.
    """

    id: str
    role: Literal["user", "assistant"]
    parts: list[MessagePart]

    @property
    def text(self) -> str:
        return "".join(part.text for part in self.parts if part.type == "text")


class ChatRequest(BaseModel):
    id: UUID  # The conversation. `useChat` sends its chat id under this name.
    persona_id: UUID
    messages: list[ChatMessage] = Field(min_length=1)

    @model_validator(mode="after")
    def last_message_is_from_user(self) -> Self:
        last = self.messages[-1]
        if last.role != "user" or not last.text.strip():
            raise ValueError("the last message must be a non-empty user message")
        return self
