from datetime import date
from typing import Optional

from fastapi.exceptions import ValidationException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.kitten import KittenColors
from config import BREED_LENGTH, KITTEN_NAME_LENGTH


class BreedCreate(BaseModel):
    name: str = Field(max_length=BREED_LENGTH)


class BreedOut(BreedCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class KittenBase(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, birth_date):
        if birth_date:
            today = date.today()
            if birth_date > today:
                raise ValidationException("Birth date can't be bigger than today")
        return birth_date

    @field_validator('name')
    @classmethod
    def validate_name(cls, name):
        if name and len(name) > KITTEN_NAME_LENGTH:
            raise ValidationException("Name can't exceed 50 characters")
        return name


class KittenCreate(KittenBase):
    color: KittenColors
    birth_date: date
    description: str
    breed_id: int


class KittenEdit(KittenBase):
    color: Optional[KittenColors] = None
    description: Optional[str] = None
    breed_id: Optional[int] = None


class KittenOut(BaseModel):
    id: int
    name: Optional[str]
    color: KittenColors
    age_in_months: int
    description: str
    breed: BreedOut

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
