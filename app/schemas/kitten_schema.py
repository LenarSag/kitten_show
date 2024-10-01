from datetime import date
from typing import Optional

from fastapi.exceptions import ValidationException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.kitten import KittenColors
from config import BREED_LENGTH, KITTEN_NAME_LENGTH


class BreedCreate(BaseModel):
    name: str = Field(max_length=BREED_LENGTH)


class BreedOut(BaseModel):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class KittenCreate(BaseModel):
    name: Optional[str] = Field(max_length=KITTEN_NAME_LENGTH)
    color: KittenColors
    birth_date: date
    description: str
    breed_id: int

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, birth_date):
        today = date.today()
        if birth_date > today:
            raise ValidationException("Birth date can't be bigger than today")
        return birth_date


class KittenOut(BaseModel):
    id: int
    name: Optional[str]
    color: KittenColors
    age_in_months: int
    description: str
    breed: BreedCreate

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
