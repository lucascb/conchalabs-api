from sqlmodel import SQLModel

from conchalabs.commons.mixins import TimestampedModelMixin, UUIDModelMixin


class UserBase(SQLModel):
    name: str
    email: str
    address: str
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
