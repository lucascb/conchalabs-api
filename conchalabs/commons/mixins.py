from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UUIDModelMixin(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
    )


class TimestampedModelMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
