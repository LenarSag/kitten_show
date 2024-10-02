from collections.abc import AsyncIterator


from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import models


DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@db:5432/postgres'


async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(check_existing_tables_and_create)


# Function to check existing tables and create if necessary
def check_existing_tables_and_create(sync_conn):
    inspector = inspect(sync_conn)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        models.Base.metadata.create_all(sync_conn)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
