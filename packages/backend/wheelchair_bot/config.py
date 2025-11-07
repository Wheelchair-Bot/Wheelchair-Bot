"""Configuration management for Wheelchair Bot backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Wheelchair Bot API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Hardware configuration
    max_speed: int = 100
    min_speed: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
