from typing import Annotated, Optional

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.breed_repository import (
    create_new_breed,
    get_breed_by_id,
    get_breed_by_name,
    get_paginated_breeds,
)
from app.db.database import get_session
from app.filters.kitten_filter import BreedFilter
from app.models.kitten import Breed
from app.models.user import User
from app.schemas.kitten_schema import BreedCreate, BreedOut
from app.security.authentication import get_current_user


breedrouter = APIRouter()


async def get_breed_or_404(session: AsyncSession, breed_id: int) -> Optional[Breed]:
    breed = await get_breed_by_id(session, breed_id)
    if breed is None:
        raise HTTPException(
            detail='Breed not found', status_code=status.HTTP_404_NOT_FOUND
        )
    return breed


@breedrouter.get('/{breed_id}', response_model=BreedOut)
async def get_breed(
    breed_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    breed = await get_breed_by_id(session, breed_id)
    if not breed:
        raise HTTPException(
            detail='Breed not found', status_code=status.HTTP_404_NOT_FOUND
        )
    return breed


@breedrouter.get('/', response_model=Page[BreedOut])
async def get_breeds(
    breed_filter: Annotated[BreedFilter, FilterDepends(BreedFilter)],
    params: Annotated[Params, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await get_paginated_breeds(session, breed_filter, params)
    return result


@breedrouter.post('/', response_model=BreedOut, status_code=status.HTTP_201_CREATED)
async def create_breed(
    breed_data: BreedCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    breed = await get_breed_by_name(session, breed_data.name)
    if breed:
        raise HTTPException(
            detail='Breed already exists', status_code=status.HTTP_400_BAD_REQUEST
        )

    new_breed = await create_new_breed(session, breed_data)
    return new_breed
