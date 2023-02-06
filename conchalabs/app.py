from fastapi import FastAPI
from fastapi_health import health

from conchalabs.dependencies.database import is_database_online
from conchalabs.user_audios.routes import router as user_audio_routes
from conchalabs.users.routes import router as users_routes


def create_app() -> FastAPI:
    app_ = FastAPI(title="Conchalabs API")

    app_.add_api_route("/health", health([is_database_online]))  # type: ignore
    app_.include_router(users_routes)
    app_.include_router(user_audio_routes)

    return app_


app = create_app()


