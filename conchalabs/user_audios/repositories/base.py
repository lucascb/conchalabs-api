import abc
from uuid import UUID

from conchalabs.user_audios.models import UserAudio


class UserAudioRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, user_audio: UserAudio) -> UserAudio:
        """Saves the user audio on the database. If the audio already exists, it will be updated.
        Raises UserAudioConflictError if attempts to save a field that conflicts with another audio on the database."""

    @abc.abstractmethod
    async def find(self, filters: dict) -> list[UserAudio]:
        """Finds audios on the database that matches the specified filters."""

    @abc.abstractmethod
    async def get_by_id(self, user_id: UUID, audio_id: UUID) -> UserAudio:
        """Gets a specific audio by user_id and audio_id.
        Raises UserAudioNotFoundError if the audio does not exist on the database."""
