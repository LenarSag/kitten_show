from datetime import date
from enum import Enum as PyEnum

from sqlalchemy import (
    case,
    Date,
    Enum,
    ForeignKey,
    func,
    String,
    Text,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)

from app.models.base import Base
from config import BREED_LENGTH, KITTEN_NAME_LENGTH


class KittenColors(PyEnum):
    WHITE = 'white'
    BLACK = 'black'
    GREY = 'grey'
    GINGER = 'ginger'


class KittenSex(PyEnum):
    MALE = 'male'
    FEMALE = 'female'


class Breed(Base):
    __tablename__ = 'breed'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(BREED_LENGTH), unique=True, nullable=False
    )

    kittens: Mapped[list['Kitten']] = relationship(
        back_populates='breed', cascade='all, delete-orphan'
    )

    def __str__(self) -> str:
        return self.name


class Kitten(Base):
    __tablename__ = 'kitten'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(KITTEN_NAME_LENGTH))
    color: Mapped[KittenColors] = mapped_column(
        Enum(KittenColors, values_callable=lambda obj: [e.value for e in obj]),
    )
    sex: Mapped[KittenSex] = mapped_column(
        Enum(KittenSex, values_callable=lambda obj: [e.value for e in obj]),
    )
    birth_date: Mapped[date] = mapped_column(Date(), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    breed_id: Mapped[int] = mapped_column(
        ForeignKey('breed.id', ondelete='CASCADE')
    )

    breed: Mapped['Breed'] = relationship(back_populates='kittens')

    @hybrid_property
    def age_in_months(self) -> int:
        if self.birth_date:
            today = date.today()
            months = (
                (today.year - self.birth_date.year) * 12
                + today.month
                - self.birth_date.month
            )
            if today.day < self.birth_date.day:
                months -= 1
            return months
        return None

    @age_in_months.expression
    def age_in_months(cls):
        today = func.now()
        return (
            (
                func.extract('year', today)
                - func.extract('year', cls.birth_date)
            ) * 12
            + (
                func.extract('month', today)
                - func.extract('month', cls.birth_date)
            )
            - case(
                (
                    func.extract('day', today)
                    < func.extract('day', cls.birth_date),
                    1,
                ),
                else_=0,
            )
        )

    @validates('birth_date')
    def validate_email(self, key, birth_date):
        today = date.today()
        if birth_date > today:
            raise ValueError("Birth date can't be bigger than today")
        return birth_date

    def __str__(self) -> str:
        return self.name
