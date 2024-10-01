from typing import Optional

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.filters.kitten_filter import BreedFilter
from app.models.kitten import Breed
from app.schemas.kitten_schema import BreedCreate


async def get_breed_by_id(session: AsyncSession, id: int) -> Optional[Breed]:
    query = select(Breed).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_breed_by_name(session: AsyncSession, name: str) -> Optional[Breed]:
    query = select(Breed).filter_by(name=name)
    result = await session.execute(query)
    return result.scalar()


async def create_new_breed(
    session: AsyncSession,
    breed_data: BreedCreate,
) -> Breed:
    new_breed = Breed(**breed_data.model_dump())
    session.add(new_breed)
    await session.commit()
    return new_breed


async def get_paginated_breeds(
    session: AsyncSession, breed_filter: BreedFilter, params: Params
):
    query = select(Breed)
    query = breed_filter.filter(query)
    query = breed_filter.sort(query)

    return await paginate(session, query, params)
