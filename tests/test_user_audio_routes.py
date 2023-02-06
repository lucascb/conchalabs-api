from http import HTTPStatus

import pytest

from conchalabs.user_audios.models import UserAudio
from conchalabs.users.models import User

USER_AUDIOS_API_URL = "/api/v1/users/{user_id}/audios"
AUDIO_API_URL = "/api/v1/users/{user_id}/audios/{audio_id}"


@pytest.fixture()
def user_payload():
    return {
        "name": "Lucas Bernardes",
        "email": "lucascbernardes@live.com",
        "address": "Brazil",
        "image": "https://example.com/img.png",
    }


@pytest.fixture()
def user_audio_payload():
    return {
        "ticks": [
            -96.33,
            -96.33,
            -93.47,
            -89.03999999999999,
            -84.61,
            -80.18,
            -75.75,
            -71.32,
            -66.89,
            -62.46,
            -58.03,
            -53.6,
            -49.17,
            -44.74,
            -40.31,
        ],
        "selected_tick": 5,
        "session_id": 3448,
        "step_count": 1,
    }


@pytest.fixture()
async def user(user_repository, user_payload):
    return await user_repository.save(User(**user_payload))


@pytest.fixture()
async def user_audio(user: User, user_audio_repository, user_audio_payload):
    return await user_audio_repository.save(
        UserAudio(user_id=user.id, **user_audio_payload)
    )


async def test_create_user_audio(
    client, user: User, user_audio_repository, user_audio_payload
):
    response = await client.post(
        USER_AUDIOS_API_URL.format(user_id=str(user.id)), json=user_audio_payload
    )

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body
    assert body["ticks"] == user_audio_payload["ticks"]
    assert body["selected_tick"] == user_audio_payload["selected_tick"]
    assert body["session_id"] == user_audio_payload["session_id"]
    assert body["step_count"] == user_audio_payload["step_count"]

    audio_db = await user_audio_repository.get_by_id(user.id, body["id"])

    assert audio_db.ticks == user_audio_payload["ticks"]
    assert audio_db.selected_tick == user_audio_payload["selected_tick"]
    assert audio_db.session_id == user_audio_payload["session_id"]
    assert audio_db.step_count == user_audio_payload["step_count"]


@pytest.mark.parametrize(
    "missing_field", ["ticks", "selected_tick", "session_id", "step_count"]
)
async def test_create_user_audio_missing_fields(
    missing_field, client, user: User, user_audio_repository, user_audio_payload
):
    del user_audio_payload[missing_field]

    response = await client.post(
        USER_AUDIOS_API_URL.format(user_id=str(user.id)), json=user_audio_payload
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["detail"][0]["msg"] == "field required"
    assert body["detail"][0]["loc"] == ["body", missing_field]

    user_audios_db = await user_audio_repository.find({"user_id": user.id})

    assert len(user_audios_db) == 0


@pytest.mark.parametrize(
    "invalid_case",
    [
        ("ticks", [-10.0], "ensure this value has at least 15 items"),
        (
            "ticks",
            [-9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9],
            "ensure this value is less than or equal to -10.0",
        ),
        (
            "ticks",
            [
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
            ],
            "ensure this value is greater than or equal to -100.0",
        ),
        ("selected_tick", -1, "ensure this value is greater than or equal to 0"),
        ("selected_tick", 15, "ensure this value is less than or equal to 14"),
        ("step_count", -1, "ensure this value is greater than or equal to 0"),
        ("step_count", 10, "ensure this value is less than or equal to 9"),
    ],
)
async def test_create_user_audio_invalid_payload(
    invalid_case, client, user: User, user_audio_repository, user_audio_payload
):
    field, invalid_value, error_message = invalid_case
    user_audio_payload[field] = invalid_value

    response = await client.post(
        USER_AUDIOS_API_URL.format(user_id=str(user.id)), json=user_audio_payload
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["detail"][0]["loc"][:2] == ["body", field]
    assert body["detail"][0]["msg"] == error_message

    user_audios_db = await user_audio_repository.find({"user_id": user.id})

    assert len(user_audios_db) == 0


async def test_create_user_audio_user_not_found(client, user: User, user_audio_payload):
    response = await client.post(
        USER_AUDIOS_API_URL.format(user_id="85423d1e-e7ba-4070-84e8-da33ddcda6dc"),
        json=user_audio_payload,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body["detail"] == "User not found"


async def test_create_user_audio_conflict_session_id(
    client, user_audio: UserAudio, user_audio_repository, user_audio_payload
):
    response = await client.post(
        USER_AUDIOS_API_URL.format(user_id=str(user_audio.user_id)),
        json=user_audio_payload,
    )

    assert response.status_code == HTTPStatus.CONFLICT

    body = response.json()

    assert body["detail"] == "Audio conflicts for user"

    user_audios_db = await user_audio_repository.find({"user_id": user_audio.user_id})

    assert len(user_audios_db) == 1


async def test_list_user_audios(client, user_audio: UserAudio):
    response = await client.get(
        USER_AUDIOS_API_URL.format(user_id=str(user_audio.user_id))
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(user_audio.id)


async def test_list_user_audios_with_query_found(client, user_audio: UserAudio):
    query = {"session_id": user_audio.session_id}

    response = await client.get(
        USER_AUDIOS_API_URL.format(user_id=str(user_audio.user_id)), params=query
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(user_audio.id)


async def test_list_user_audios_with_query_not_found(client, user_audio: UserAudio):
    query = {"session_id": 123}

    response = await client.get(
        USER_AUDIOS_API_URL.format(user_id=str(user_audio.user_id)), params=query
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert len(body) == 0


async def test_get_user_audio_by_id(client, user_audio: UserAudio):
    response = await client.get(
        AUDIO_API_URL.format(
            user_id=str(user_audio.user_id), audio_id=str(user_audio.id)
        )
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body["id"] == str(user_audio.id)


async def test_get_user_audio_by_id_not_found(client, user_audio: UserAudio):
    response = await client.get(
        AUDIO_API_URL.format(
            user_id=str(user_audio.user_id),
            audio_id="85423d1e-e7ba-4070-84e8-da33ddcda6dc",
        )
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body["detail"] == "Audio not found"


async def test_get_user_audio_by_id_invalid_uuid(client, user_audio: UserAudio):
    response = await client.get(
        AUDIO_API_URL.format(
            user_id=str(user_audio.user_id),
            audio_id="1",
        )
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["detail"][0]["msg"] == "value is not a valid uuid"
    assert body["detail"][0]["loc"] == ["path", "audio_id"]


@pytest.mark.parametrize(
    "update_payload",
    [
        {
            "ticks": [
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
            ]
        },
        {"selected_tick": 14},
        {"session_id": 0},
        {"step_count": 9},
    ],
)
async def test_update_user_audio_by_id(
    update_payload, client, user_audio: UserAudio, db_session
):
    response = await client.patch(
        AUDIO_API_URL.format(
            user_id=str(user_audio.user_id), audio_id=str(user_audio.id)
        ),
        json=update_payload,
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert all(body[field] == value for field, value in update_payload.items())

    await db_session.refresh(user_audio)

    assert all(
        getattr(user_audio, field) == value for field, value in update_payload.items()
    )


async def test_update_user_audio_by_id_not_found(client, user_audio: UserAudio):
    update_payload = {"session_id": 0}

    response = await client.patch(
        AUDIO_API_URL.format(
            user_id=str(user_audio.user_id),
            audio_id="85423d1e-e7ba-4070-84e8-da33ddcda6dc",
        ),
        json=update_payload,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body["detail"] == "Audio not found"


@pytest.mark.parametrize(
    "invalid_case",
    [
        ("ticks", [-10.0], "ensure this value has at least 15 items"),
        (
            "ticks",
            [-9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9, -9],
            "ensure this value is less than or equal to -10.0",
        ),
        (
            "ticks",
            [
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
                -101,
            ],
            "ensure this value is greater than or equal to -100.0",
        ),
        ("selected_tick", -1, "ensure this value is greater than or equal to 0"),
        ("selected_tick", 15, "ensure this value is less than or equal to 14"),
        ("step_count", -1, "ensure this value is greater than or equal to 0"),
        ("step_count", 10, "ensure this value is less than or equal to 9"),
    ],
)
async def test_update_user_audio_by_id_invalid_payload(
    invalid_case, client, user_audio: UserAudio
):
    field, invalid_value, error_message = invalid_case
    update_payload = {field: invalid_value}

    response = await client.patch(
        AUDIO_API_URL.format(
            user_id=str(user_audio.user_id), audio_id=str(user_audio.id)
        ),
        json=update_payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["detail"][0]["loc"][:2] == ["body", field]
    assert body["detail"][0]["msg"] == error_message


async def test_update_user_audio_by_id_conflicts(
    client, user_audio: UserAudio, user_audio_repository
):
    second_user_audio = await user_audio_repository.save(
        UserAudio(
            user_id=user_audio.user_id,
            ticks=[
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
            ],
            selected_tick=14,
            session_id=0,
            step_count=0,
        )
    )

    update_payload = {"session_id": user_audio.session_id}

    response = await client.patch(
        AUDIO_API_URL.format(
            user_id=str(second_user_audio.user_id),
            audio_id=str(second_user_audio.id),
        ),
        json=update_payload,
    )

    assert response.status_code == HTTPStatus.CONFLICT

    body = response.json()

    assert body["detail"] == "Audio conflicts for user"
