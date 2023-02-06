from sqlmodel import JSON, Column, Field, SQLModel, UniqueConstraint

from conchalabs.commons.mixins import UUID, TimestampedModelMixin, UUIDModelMixin


class UserAudioBase(SQLModel):
    __table_args__ = (UniqueConstraint("step_count", "session_id"),)

    ticks: list[float] = Field(
        sa_column=Column(JSON), min_items=15, max_items=15, ge=-100.0, le=-10.0
    )
    selected_tick: int = Field(ge=0, le=14)
    session_id: int = Field(unique=True)
    step_count: int = Field(ge=0, le=9)


class UserAudio(UserAudioBase, UUIDModelMixin, TimestampedModelMixin, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id")


class UserAudioCreate(UserAudioBase):
    pass


class UserAudioUpdate(SQLModel):
    ticks: list[float] | None = Field(min_items=15, max_items=15, ge=-100.0, le=-10.0)
    selected_tick: int | None = Field(ge=0, le=14)
    session_id: int | None
    step_count: int | None = Field(ge=0, le=9)
