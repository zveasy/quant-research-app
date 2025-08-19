"""Configuration management for the equity-options-research project."""
from functools import lru_cache
from pydantic import BaseSettings, Field, ValidationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    polygon_api_key: str = Field(..., env="POLYGON_API_KEY")


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings.

    Raises
    ------
    RuntimeError
        If the required environment variable is missing.
    """
    try:
        return Settings()
    except ValidationError as exc:  # pragma: no cover - explicit for clarity
        raise RuntimeError(
            "POLYGON_API_KEY environment variable is required"
        ) from exc
