from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import UUID

from app.core.errors import ConflictError, NotFoundError
from app.repositories.json_file import JsonFile
from app.schemas.chat import ChatMessage
from app.schemas.conversation import Conversation

TITLE_LENGTH = 60


class ConversationRepository:
    """Stores chat history in one JSON file. See PersonaRepository for the lock."""

    def __init__(self, path: Path) -> None:
        self._file = JsonFile(path, Conversation)
        self._lock = Lock()

    def list_for_persona(self, persona_id: UUID) -> list[Conversation]:
        conversations = [c for c in self._file.read() if c.persona_id == persona_id]
        return sorted(conversations, key=lambda c: c.updated_at, reverse=True)

    def get(self, conversation_id: UUID) -> Conversation:
        for conversation in self._file.read():
            if conversation.id == conversation_id:
                return conversation
        raise NotFoundError(f"Conversation {conversation_id} not found")

    def save_messages(
        self, conversation_id: UUID, persona_id: UUID, messages: list[ChatMessage]
    ) -> None:
        """Creates the conversation on its first message, then keeps it updated."""
        with self._lock:
            conversations = self._file.read()
            existing = next((c for c in conversations if c.id == conversation_id), None)
            if existing and existing.persona_id != persona_id:
                raise ConflictError("Conversation belongs to another persona")

            first_text = next(m.text for m in messages if m.role == "user")
            saved = Conversation(
                id=conversation_id,
                persona_id=persona_id,
                title=existing.title if existing else first_text[:TITLE_LENGTH],
                updated_at=datetime.now(UTC),
                messages=messages,
            )
            others = [c for c in conversations if c.id != conversation_id]
            self._file.write([*others, saved])

    def add_reply(self, conversation_id: UUID, reply: ChatMessage) -> None:
        """Saves a finished reply. A stopped reply is kept with the text so far."""
        if not reply.text:
            return
        with self._lock:
            conversations = self._file.read()
            for conversation in conversations:
                already_saved = any(m.id == reply.id for m in conversation.messages)
                if conversation.id == conversation_id and not already_saved:
                    conversation.messages.append(reply)
                    conversation.updated_at = datetime.now(UTC)
                    self._file.write(conversations)
                    return

    def delete(self, conversation_id: UUID) -> None:
        with self._lock:
            conversations = self._file.read()
            remaining = [c for c in conversations if c.id != conversation_id]
            if len(remaining) == len(conversations):
                raise NotFoundError(f"Conversation {conversation_id} not found")
            self._file.write(remaining)

    def delete_for_persona(self, persona_id: UUID) -> None:
        with self._lock:
            conversations = self._file.read()
            self._file.write([c for c in conversations if c.persona_id != persona_id])
