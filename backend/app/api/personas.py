from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import PersonaRepo
from app.core.responses import ApiResponse
from app.schemas.persona import Persona, PersonaCreate

router = APIRouter(prefix="/personas", tags=["personas"])

# These are plain `def`, not `async def`: file I/O blocks, so FastAPI runs them
# in its thread pool and the event loop stays free for streaming chats.


@router.get("")
def list_personas(repo: PersonaRepo) -> ApiResponse[list[Persona]]:
    return ApiResponse(data=repo.list_all())


@router.post("", status_code=status.HTTP_201_CREATED)
def create_persona(body: PersonaCreate, repo: PersonaRepo) -> ApiResponse[Persona]:
    return ApiResponse(data=repo.create(body))


@router.get("/{persona_id}")
def get_persona(persona_id: UUID, repo: PersonaRepo) -> ApiResponse[Persona]:
    return ApiResponse(data=repo.get(persona_id))


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: UUID, repo: PersonaRepo) -> None:
    repo.delete(persona_id)
