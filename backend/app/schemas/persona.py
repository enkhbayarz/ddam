from datetime import date
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PersonaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    birthdate: date
    lived_place: str = Field(min_length=1, max_length=200)
    details: str = Field(min_length=1, max_length=2000)
    gender: Literal["male", "female", "other"]

    @field_validator("birthdate")
    @classmethod
    def birthdate_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("birthdate cannot be in the future")
        return value


class Persona(PersonaCreate):
    id: UUID = Field(default_factory=uuid4)
