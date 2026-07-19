"""Core settings and dependency injection."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Kerykeion Astrology API"
    app_version: str = "1.1.0"
    api_key: str = ""
    cors_origins: str = "*"
    rate_limit: str = "100/minute"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
