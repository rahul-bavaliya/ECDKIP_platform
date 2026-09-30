from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import get_logger

logger = get_logger()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Cloud Document & Knowledge Intelligence Platform"
    API_V1_STR: str = "/api/v1"

    # Database Configuration (fetched dynamically from .env)
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        postgres_url = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        logger.info(postgres_url)
        return postgres_url

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
