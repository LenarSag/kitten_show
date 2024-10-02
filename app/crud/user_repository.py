from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user_schema import UserCreate


async def get_user_by_id(
    session: AsyncSession, id: uuid.UUID
) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_user_by_username(
    session: AsyncSession, username: str
) -> Optional[User]:
    query = select(User).filter_by(username=username)
    result = await session.execute(query)
    return result.scalar()


async def create_new_user(
    session: AsyncSession,
    user_data: UserCreate,
) -> User:
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user
