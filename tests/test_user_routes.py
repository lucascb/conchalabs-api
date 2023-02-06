from http import HTTPStatus

import pytest

from conchalabs.users.errors import UserNotFoundError
from conchalabs.users.models import User

USERS_API_URL = "/api/v1/users"


@pytest.fixture()
def user_payload():
    return {
        "name": "Lucas Bernardes",
        "email": "lucascbernardes@live.com",
        "address": "Brazil",
        "image": "https://example.com/img.png",
    }


@pytest.fixture()
async def user(user_repository, user_payload):
    return await user_repository.save(User(**user_payload))


async def test_create_user(client, user_repository, user_payload):
    response = await client.post(USERS_API_URL, json=user_payload)

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert "id" in body
    assert body["name"] == user_payload["name"]
    assert body["email"] == user_payload["email"]
    assert body["address"] == user_payload["address"]
    assert body["image"] == user_payload["image"]

    user_db = await user_repository.get_by_id(body["id"])

    assert user_db.name == user_payload["name"]
    assert user_db.email == user_payload["email"]
    assert user_db.address == user_payload["address"]
    assert user_db.image == user_payload["image"]


@pytest.mark.parametrize("missing_field", ["name", "email", "address", "image"])
async def test_create_user_missing_fields(
    missing_field, client, user_repository, user_payload
):
    del user_payload[missing_field]

    response = await client.post(USERS_API_URL, json=user_payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["detail"][0]["msg"] == "field required"
    assert body["detail"][0]["loc"] == ["body", missing_field]

    users_db = await user_repository.find({})

    assert len(users_db) == 0


async def test_list_users_api(client, user: User):
    response = await client.get(USERS_API_URL)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(user.id)


@pytest.mark.parametrize(
    "query",
    [
        {"name": "Lucas Bernardes"},
        {"email": "lucascbernardes@live.com"},
        {"address": "Brazil"},
    ],
)
async def test_list_users_api_with_query_found(query, client, user: User):
    response = await client.get(USERS_API_URL, params=query)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(user.id)


@pytest.mark.parametrize(
    "query", [{"name": "John Doe"}, {"email": "john.doe@email.com"}, {"address": "USA"}]
)
async def test_list_users_api_with_query_not_found(query, client, user: User):
    response = await client.get(USERS_API_URL, params=query)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert len(body) == 0


async def test_get_user_by_id(client, user: User):
    response = await client.get(f"{USERS_API_URL}/{str(user.id)}")

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body["id"] == str(user.id)


async def test_get_user_by_id_not_found(client, user: User):
    response = await client.get(f"{USERS_API_URL}/85423d1e-e7ba-4070-84e8-da33ddcda6dc")

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body["detail"] == "User not found"


async def test_get_user_by_id_invalid_uuid(client, user: User):
    response = await client.get(f"{USERS_API_URL}/1")

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["detail"][0]["msg"] == "value is not a valid uuid"
    assert body["detail"][0]["loc"] == ["path", "user_id"]


@pytest.mark.parametrize(
    "update_payload",
    [
        {"name": "John Doe"},
        {"email": "john.doe@email.com"},
        {"address": "USA"},
        {"image": "https://example.com/other-img.png"},
    ],
)
async def test_update_user_by_id(update_payload, client, user: User, db_session):
    response = await client.patch(
        f"{USERS_API_URL}/{str(user.id)}", json=update_payload
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert all(body[field] == value for field, value in update_payload.items())

    await db_session.refresh(user)

    assert all(getattr(user, field) == value for field, value in update_payload.items())


async def test_update_user_by_id_not_found(client, user: User, db_session):
    update_payload = {"name": "John Doe"}

    response = await client.patch(
        f"{USERS_API_URL}/85423d1e-e7ba-4070-84e8-da33ddcda6dc",
        json=update_payload,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body["detail"] == "User not found"


async def test_delete_user_by_id(client, user: User, user_repository):
    response = await client.delete(f"{USERS_API_URL}/{str(user.id)}")

    assert response.status_code == HTTPStatus.NO_CONTENT

    with pytest.raises(UserNotFoundError):
        await user_repository.get_by_id(user.id)


async def test_delete_user_by_id_not_found(client, user: User, user_repository):
    response = await client.delete(
        f"{USERS_API_URL}/85423d1e-e7ba-4070-84e8-da33ddcda6dc"
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body["detail"] == "User not found"
