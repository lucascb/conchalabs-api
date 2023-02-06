from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from conchalabs.dependencies.database import get_user_repository
from conchalabs.users.errors import UserNotFoundError
from conchalabs.users.models import User, UserCreate, UserUpdate
from conchalabs.users.repositories.base import UserRepository

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


@router.post("", status_code=HTTPStatus.CREATED, response_model=User)
async def create_user(
    user_data: UserCreate,
    repository: UserRepository = Depends(get_user_repository),
):
    user = User(
        name=user_data.name,
        email=user_data.email,
        address=user_data.address,
        image=user_data.image,
    )

    return await repository.save(user)


@router.get("", response_model=list[User])
async def list_users(
    name: str | None = None,
    email: str | None = None,
    address: str | None = None,
    repository: UserRepository = Depends(get_user_repository),
):
    filters = {}

    if name is not None:
        filters["name"] = name
    if email is not None:
        filters["email"] = email
    if address is not None:
        filters["address"] = address

    return await repository.find(filters)


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: UUID,
    repository: UserRepository = Depends(get_user_repository),
):
    try:
        return await repository.get_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )


@router.patch("/{user_id}", response_model=User)
async def update_user_by_id(
    user_id: UUID,
    user_data: UserUpdate,
    repository: UserRepository = Depends(get_user_repository),
):
    user = await get_user_by_id(user_id, repository)

    for field, val in user_data.dict(exclude_unset=True).items():
        setattr(user, field, val)

    return await repository.save(user)


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user_by_id(
    user_id: UUID,
    repository: UserRepository = Depends(get_user_repository),
):
    user = await get_user_by_id(user_id, repository)
    await repository.delete(user)
