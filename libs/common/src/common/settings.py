"""Typed application settings, loaded from the environment with the ``ECI_`` prefix."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Process-wide configuration shared by every service."""

    model_config = SettingsConfigDict(env_prefix="ECI_", extra="ignore")

    service_name: str = "eci"
    environment: str = "dev"
    log_level: str = "INFO"
    aws_region: str = "us-east-1"
    kafka_bootstrap_servers: str = "localhost:9092"
    temporal_address: str = "localhost:7233"
    otlp_endpoint: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()
