from http import HTTPStatus

from conchalabs.dependencies.database import get_db_session

HEALTHCHECK_API_URL = "/health"


async def test_healthcheck_ok(client):
    response = await client.get(HEALTHCHECK_API_URL)

    assert response.status_code == HTTPStatus.OK


async def test_healthcheck_database_down(test_app, client):
    class DisconnectedSession:
        async def execute(self, *args, **kwargs):
            raise ConnectionRefusedError()

    test_app.dependency_overrides[get_db_session] = lambda: DisconnectedSession()

    response = await client.get(HEALTHCHECK_API_URL)

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
