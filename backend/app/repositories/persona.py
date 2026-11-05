from pathlib import Path
from threading import Lock
from uuid import UUID

from app.core.errors import ConflictError, NotFoundError
from app.repositories.json_file import JsonFile
from app.schemas.persona import Persona, PersonaCreate


class PersonaRepository:
    """Stores personas in one JSON file.

    Sync endpoints run in a thread pool, so two writes can overlap. The lock
    stops one write from losing the other's change.
    """

    def __init__(self, path: Path) -> None:
        self._file = JsonFile(path, Persona)
        self._lock = Lock()

    def list_all(self) -> list[Persona]:
        return self._file.read()

    def get(self, persona_id: UUID) -> Persona:
        for persona in self.list_all():
            if persona.id == persona_id:
                return persona
        raise NotFoundError(f"Persona {persona_id} not found")

    def create(self, data: PersonaCreate) -> Persona:
        with self._lock:
            personas = self.list_all()
            if any(p.name.casefold() == data.name.casefold() for p in personas):
                raise ConflictError(f"Persona '{data.name}' already exists")
            persona = Persona(**data.model_dump())
            self._file.write([*personas, persona])
        return persona

    def delete(self, persona_id: UUID) -> None:
        with self._lock:
            personas = self.list_all()
            remaining = [p for p in personas if p.id != persona_id]
            if len(remaining) == len(personas):
                raise NotFoundError(f"Persona {persona_id} not found")
            self._file.write(remaining)
