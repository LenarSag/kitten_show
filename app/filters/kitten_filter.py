from typing import Optional
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.kitten import Breed, Kitten, KittenColors


class BreedFilter(Filter):
    name: Optional[str] = None
    name__ilike: Optional[str] = None
    name__like: Optional[str] = None

    order_by: list[str] = ['name']

    class Constants(Filter.Constants):
        model = Breed


class KittenFilter(Filter):
    color: Optional[KittenColors] = None
    age_in_months__lt: Optional[int] = None
    age_in_months__gt: Optional[int] = None
    breed: Optional[BreedFilter] = FilterDepends(with_prefix('breed', BreedFilter))

    order_by: list[str] = ['name']

    class Constants(Filter.Constants):
        model = Kitten
