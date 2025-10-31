"""Application configuration."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    environment: str = "development"
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> str:
        """Parse CORS origins from string or list."""
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Database
    database_url: str = "sqlite:///./tradewedge.db"

    # Data
    data_cache_dir: Path = Path("./data/cached_data")
    vtsax_ticker: str = "VTSAX"

    # Logging
    log_level: str = "INFO"

    def __init__(self, **kwargs):  # type: ignore
        """Initialize settings and ensure directories exist."""
        super().__init__(**kwargs)
        self.data_cache_dir.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
