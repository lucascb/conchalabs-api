import abc
from uuid import UUID

from conchalabs.users.models import User


class UserRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, user: User) -> User:
        """Saves the user on the database.tf. If the user already exists, it will be updated."""

    @abc.abstractmethod
    async def find(self, filters: dict) -> list[User]:
        """Finds users on the database.tf that matches the specified filters."""

    @abc.abstractmethod
    async def get_by_id(self, user_id: UUID) -> User:
        """Gets a specific user by id. Raises UserNotFoundError if the user does not exist on the database.tf."""

    @abc.abstractmethod
    async def delete(self, user: User):
        """Deletes the user on the database.tf."""
