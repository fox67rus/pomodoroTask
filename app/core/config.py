from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pomodoro Task Tracker"
    app_env: str = "development"
    secret_key: str = "local-development-secret-key-do-not-use-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./task_tracker.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
