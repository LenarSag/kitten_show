from datetime import date
from typing import Optional

from fastapi.exceptions import ValidationException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.kitten import KittenColors, KittenSex
from config import BREED_LENGTH, KITTEN_NAME_LENGTH, MAX_KITTEN_AGE


class BreedCreate(BaseModel):
    name: str = Field(max_length=BREED_LENGTH, description='Breed name')


class BreedOut(BreedCreate):
    id: int = Field(..., description='Breed id')

    model_config = ConfigDict(
        from_attributes=True,
    )


class KittenBase(BaseModel):
    name: Optional[str] = Field(
        None, max_length=KITTEN_NAME_LENGTH, description='Kitten name'
    )
    birth_date: Optional[date] = Field(None, description='Birth date')

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, birth_date):
        if birth_date:
            today = date.today()
            if birth_date > today:
                raise ValidationException("Birth date can't be later than today")
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age > MAX_KITTEN_AGE:
                raise ValidationException('Age must be at most 20 years old.')
            return birth_date


class KittenCreate(KittenBase):
    color: KittenColors = Field(description='Kitten colors')
    sex: KittenSex = Field(description='Kitten sex')
    birth_date: date = Field(..., description='Kitten birth date')
    description: str = Field(..., description='Kitten description')
    breed_id: int = Field(..., description='Breed id')


class KittenEdit(KittenBase):
    color: Optional[KittenColors] = Field(None, description='Kitten color')
    sex: Optional[KittenSex] = Field(None, description='Kitten sex')
    description: Optional[str] = Field(None, description='Kitten description')
    breed_id: Optional[int] = Field(None, description='Breed id')


class KittenOut(BaseModel):
    id: int = Field(..., description='Kitten id')
    name: Optional[str] = Field(None, description='Kitten name')
    color: KittenColors = Field(description='Kitten color')
    sex: KittenSex = Field(description='Kitten sex')
    age_in_months: int = Field(..., description='Kitten age in months')
    description: str = Field(..., description='Kitten description')
    breed: BreedOut = Field(..., description='Kitten breed')

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
