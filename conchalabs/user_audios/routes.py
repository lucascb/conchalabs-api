from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from conchalabs.dependencies.database import (
    get_user_audio_repository,
    get_user_repository,
)
from conchalabs.user_audios.errors import UserAudioConflictError, UserAudioNotFoundError
from conchalabs.user_audios.models import UserAudio, UserAudioCreate, UserAudioUpdate
from conchalabs.user_audios.repositories.base import UserAudioRepository
from conchalabs.users.repositories.base import UserRepository
from conchalabs.users.routes import get_user_by_id

router = APIRouter(
    prefix="/api/v1/users/{user_id}/audios",
    tags=["User Audios"],
)


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=UserAudio,
)
async def create_user_audio(
    user_id: UUID,
    audio_data: UserAudioCreate,
    user_repository: UserRepository = Depends(get_user_repository),
    user_audio_repository: UserAudioRepository = Depends(get_user_audio_repository),
):
    user = await get_user_by_id(user_id, user_repository)

    audio = UserAudio(
        user_id=user.id,
        ticks=audio_data.ticks,
        session_id=audio_data.session_id,
        selected_tick=audio_data.selected_tick,
        step_count=audio_data.step_count,
    )

    try:
        return await user_audio_repository.save(audio)
    except UserAudioConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Audio conflicts for user",
        )


@router.get(
    "",
    response_model=list[UserAudio],
)
async def list_user_audios(
    user_id: UUID,
    session_id: int | None = None,
    user_repository: UserRepository = Depends(get_user_repository),
    user_audio_repository: UserAudioRepository = Depends(get_user_audio_repository),
):
    user = await get_user_by_id(user_id, user_repository)

    filters = {"user_id": user.id}
    if session_id is not None:
        filters["session_id"] = session_id

    return await user_audio_repository.find(filters)


@router.get("/{audio_id}", response_model=UserAudio)
async def get_user_audio_by_id(
    user_id: UUID,
    audio_id: UUID,
    user_audio_repository: UserAudioRepository = Depends(get_user_audio_repository),
):
    try:
        return await user_audio_repository.get_by_id(user_id, audio_id)
    except UserAudioNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Audio not found",
        )


@router.patch("/{audio_id}", response_model=UserAudio)
async def update_user_audio_by_id(
    user_id: UUID,
    audio_id: UUID,
    audio_data: UserAudioUpdate,
    user_audio_repository: UserAudioRepository = Depends(get_user_audio_repository),
):
    user_audio = await get_user_audio_by_id(user_id, audio_id, user_audio_repository)

    for field, val in audio_data.dict(exclude_unset=True).items():
        setattr(user_audio, field, val)

    try:
        return await user_audio_repository.save(user_audio)
    except UserAudioConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Audio conflicts for user",
        )
