import asyncio
import contextlib

import pytest
from httpx import AsyncClient
from sqlmodel import delete

from conchalabs.app import create_app
from conchalabs.dependencies.database import (
    get_db_session,
    get_user_audio_repository,
    get_user_repository,
)
from conchalabs.settings import settings
from conchalabs.user_audios.models import UserAudio
from conchalabs.users.models import User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def test_app():
    return create_app()


@pytest.fixture()
async def client(test_app):
    async with AsyncClient(app=test_app, base_url=settings.api_base_url) as _client:
        yield _client


@pytest.fixture()
async def db_session():
    _get_db_session = contextlib.asynccontextmanager(get_db_session)
    async with _get_db_session() as session:
        yield session


@pytest.fixture()
def user_repository(db_session):
    return get_user_repository(db_session)


@pytest.fixture()
def user_audio_repository(db_session):
    return get_user_audio_repository(db_session)


@pytest.fixture(autouse=True)
async def isolate_tests(db_session):
    try:
        yield
    finally:
        await db_session.exec(delete(UserAudio))
        await db_session.exec(delete(User))
        await db_session.commit()
