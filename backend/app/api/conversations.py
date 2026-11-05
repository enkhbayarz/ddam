from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import ConversationRepo
from app.core.responses import ApiResponse
from app.schemas.conversation import Conversation, ConversationSummary

router = APIRouter(tags=["conversations"])


@router.get("/personas/{persona_id}/conversations")
def list_conversations(
    persona_id: UUID, repo: ConversationRepo
) -> ApiResponse[list[ConversationSummary]]:
    return ApiResponse(data=repo.list_for_persona(persona_id))


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: UUID, repo: ConversationRepo
) -> ApiResponse[Conversation]:
    return ApiResponse(data=repo.get(conversation_id))


@router.delete(
    "/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_conversation(conversation_id: UUID, repo: ConversationRepo) -> None:
    repo.delete(conversation_id)
