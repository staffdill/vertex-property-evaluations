"""Application configuration via pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables with WISE_ prefix."""

    model_config = SettingsConfigDict(env_prefix="WISE_")

    db_path: Path = Path("db/wise.db")
    debug: bool = False
    app_version: str = "0.1.0"


settings = Settings()
