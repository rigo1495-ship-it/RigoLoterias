from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RigoLoterias"
    api_prefix: str = "/api/v1"
    database_url: str = Field(
        default=f"sqlite:///{Path(__file__).resolve().parents[2] / 'rigoloterias.sqlite3'}"
    )
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
