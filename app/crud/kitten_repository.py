from typing import Optional

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.filters.kitten_filter import KittenFilter
from app.models.kitten import Kitten


async def get_kitten_by_id(session: AsyncSession, id: int) -> Optional[Kitten]:
    query = select(Kitten).filter_by(id=id).options(selectinload(Kitten.breed))
    result = await session.execute(query)
    return result.scalar()


async def create_new_kitten(
    session: AsyncSession,
    kitten_data,
) -> Kitten:
    new_kitten = Kitten(**kitten_data.model_dump())
    session.add(new_kitten)
    await session.commit()
    await session.refresh(new_kitten, attribute_names=('breed',))
    return new_kitten


async def get_paginated_kittens(
    session: AsyncSession, kitten_filter: KittenFilter, params: Params
):
    query = select(Kitten).join(Kitten.breed).options(selectinload(Kitten.breed))
    query = kitten_filter.filter(query)
    query = kitten_filter.sort(query)

    return await paginate(session, query, params)


async def update_lesson_data(
    session: AsyncSession, kitten: Kitten, new_kitten_data
) -> Kitten:
    update_data = new_kitten_data.model_dump()
    for key, value in update_data.items():
        if value:
            setattr(kitten, key, value)
    await session.commit()
    await session.refresh(kitten)
    return kitten