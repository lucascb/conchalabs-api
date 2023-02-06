from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from conchalabs.user_audios.errors import UserAudioConflictError, UserAudioNotFoundError
from conchalabs.user_audios.models import UserAudio
from conchalabs.user_audios.repositories.base import UserAudioRepository


class PostgresUserAudioRepository(UserAudioRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user_audio: UserAudio) -> UserAudio:
        user_audio.updated_at = datetime.utcnow()

        self._session.add(user_audio)

        try:
            await self._session.commit()
        except IntegrityError as error:
            raise UserAudioConflictError() from error

        await self._session.refresh(user_audio)

        return user_audio

    async def find(self, filters: dict) -> list[UserAudio]:
        query = select(UserAudio)

        for field, val in filters.items():
            query = query.where(getattr(UserAudio, field) == val)

        user_audios = await self._session.execute(query)
        return user_audios.scalars().all()

    async def get_by_id(self, user_id: UUID, audio_id: UUID) -> UserAudio:
        query = select(UserAudio).where(
            (UserAudio.id == audio_id) & (UserAudio.user_id == user_id)
        )

        result = await self._session.execute(query)
        audio = result.scalars().first()

        if audio is None:
            raise UserAudioNotFoundError()

        return audio
