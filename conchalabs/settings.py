from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    api_base_url: str = "http://localhost:8000"
    db_ping_timeout: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
