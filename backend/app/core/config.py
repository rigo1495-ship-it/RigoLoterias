from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RigoLoterias"
    environment: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api/v1"
    database_url: str = Field(
        default=f"sqlite:///{Path(__file__).resolve().parents[2] / 'rigoloterias.sqlite3'}"
    )
    cors_origins: tuple[str, ...] = (
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    )
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> tuple[str, ...]:
        if isinstance(value, str):
            return tuple(origin.strip() for origin in value.split(",") if origin.strip())
        if isinstance(value, (list, tuple)) and all(isinstance(origin, str) for origin in value):
            return tuple(value)
        raise ValueError("cors_origins must be a comma-separated string or a list of origins")


@lru_cache
def get_settings() -> Settings:
    return Settings()
