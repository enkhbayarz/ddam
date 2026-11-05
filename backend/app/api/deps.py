from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import get_settings
from app.repositories.persona import PersonaRepository


@lru_cache  # One shared instance, so every request uses the same lock.
def get_persona_repository() -> PersonaRepository:
    return PersonaRepository(get_settings().personas_path)


PersonaRepo = Annotated[PersonaRepository, Depends(get_persona_repository)]
