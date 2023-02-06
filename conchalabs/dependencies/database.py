import asyncio

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from conchalabs.settings import settings
from conchalabs.user_audios.repositories.base import UserAudioRepository
from conchalabs.user_audios.repositories.postgres import PostgresUserAudioRepository
from conchalabs.users.repositories.base import UserRepository
from conchalabs.users.repositories.postgres import PostgresUserRepository

engine = create_async_engine(settings.database_url)


async def get_db_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return PostgresUserRepository(session)


def get_user_audio_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserAudioRepository:
    return PostgresUserAudioRepository(session)


async def is_database_online(session: AsyncSession = Depends(get_db_session)) -> bool:
    try:
        await asyncio.wait_for(
            session.execute(text("SELECT 1")), timeout=settings.db_ping_timeout
        )
    except (SQLAlchemyError, ConnectionRefusedError, TimeoutError):
        return False

    return True
