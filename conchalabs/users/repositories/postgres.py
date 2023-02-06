from datetime import datetime
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from conchalabs.users.errors import UserNotFoundError
from conchalabs.users.models import User
from conchalabs.users.repositories.base import UserRepository


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> User:
        user.updated_at = datetime.utcnow()

        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)

        return user

    async def find(self, filters: dict) -> list[User]:
        query = select(User)

        for field, val in filters.items():
            query = query.where(getattr(User, field) == val)

        users = await self._session.execute(query)
        return users.scalars().all()

    async def get_by_id(self, user_id: UUID) -> User:
        query = select(User).where(User.id == user_id)

        result = await self._session.execute(query)
        user = result.scalars().first()

        if user is None:
            raise UserNotFoundError()

        return user

    async def delete(self, user: User):
        await self._session.delete(user)
        await self._session.commit()
