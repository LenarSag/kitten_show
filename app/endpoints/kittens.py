from typing import Annotated, Optional

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.breed_repository import get_breed_by_id
from app.crud.kitten_repository import (
    create_new_kitten,
    get_kitten_by_id,
    get_paginated_kittens,
)
from app.db.database import get_session
from app.filters.kitten_filter import KittenFilter
from app.models.kitten import Kitten
from app.models.user import User
from app.schemas.kitten_schema import KittenCreate, KittenOut
from app.security.authentication import get_current_user


kittenrouter = APIRouter()


async def get_kitten_or_404(session: AsyncSession, kitten_id: int) -> Optional[Kitten]:
    kitten = await get_kitten_by_id(session, kitten_id)
    if kitten is None:
        raise HTTPException(
            detail='Kitten not found', status_code=status.HTTP_404_NOT_FOUND
        )
    return kitten


@kittenrouter.get('/{kitten_id}', response_model=KittenOut)
async def get_kitten(
    kitten_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    kitten = await get_kitten_or_404(session, kitten_id)
    return kitten


@kittenrouter.get('/', response_model=Page[KittenOut])
async def get_kittens(
    kitten_filter: Annotated[KittenFilter, FilterDepends(KittenFilter)],
    params: Annotated[Params, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await get_paginated_kittens(session, kitten_filter, params)
    return result


@kittenrouter.post('/', response_model=KittenOut, status_code=status.HTTP_201_CREATED)
async def create_kitten(
    kitten_data: KittenCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    breed = await get_breed_by_id(session, kitten_data.breed_id)
    if breed is None:
        raise HTTPException(
            detail='Breed not found', status_code=status.HTTP_400_BAD_REQUEST
        )
    new_kitten = await create_new_kitten(session, kitten_data)
    return new_kitten


@kittenrouter.patch('/{kitten_id}')
async def update_kitten():
    pass


@kittenrouter.delete('/{kitten_id}')
async def delete_kitten():
    pass
