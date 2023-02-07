from sqlmodel import Field, SQLModel

from conchalabs.commons.mixins import TimestampedModelMixin, UUIDModelMixin


class UserBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(index=True)
    address: str = Field(index=True)
    image: str


class User(UserBase, UUIDModelMixin, TimestampedModelMixin, table=True):
    pass


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    name: str | None
    email: str | None
    address: str | None
    image: str | None
