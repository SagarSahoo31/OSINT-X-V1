"""Application configuration and environment settings for OSINT-X."""

import json
from typing import Any, List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for OSINT-X."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Information
    APP_NAME: str = "OSINT-X"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-this-to-a-secure-random-secret-key-in-production-min-32-chars"
    API_V1_STR: str = "/api/v1"

    # CORS (Allows frontend on localhost, Vercel, and Render)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # PostgreSQL Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "osintx"
    POSTGRES_USER: str = "osintx_user"
    POSTGRES_PASSWORD: str = "osintx_secure_password"
    DATABASE_URL: str = "postgresql+asyncpg://osintx_user:osintx_secure_password@localhost:5432/osintx"
    DATABASE_SYNC_URL: str = "postgresql://osintx_user:osintx_secure_password@localhost:5432/osintx"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_async_database_url(cls, v: str) -> str:
        """Ensures asyncpg driver prefix is applied for SQLAlchemy async engine."""
        if not v:
            return v
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("DATABASE_SYNC_URL", mode="before")
    @classmethod
    def assemble_sync_database_url(cls, v: str, values: Any) -> str:
        """Ensures standard postgresql prefix is applied for Celery and Alembic."""
        if not v:
            return v
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        if "+asyncpg" in v:
            return v.replace("+asyncpg", "")
        return v

    # Redis Broker & Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    @field_validator("REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def normalize_redis_url(cls, v: str) -> str:
        if v and v.startswith("rediss://"):
            # SSL Redis connections (e.g. Render / Upstash)
            return v
        return v

    # Neo4j Graph Database
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "osintx_neo4j_password"

    # Ollama Local AI
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_TIMEOUT_SECONDS: int = 60

    # Collector Safety & Execution Controls
    COLLECTOR_TIMEOUT_SECONDS: int = 180
    MAX_CONCURRENT_COLLECTORS: int = 5
    MAX_SUBPROCESS_MEMORY_MB: int = 512
    ENABLE_STRICT_TARGET_VALIDATION: bool = True
    ALLOW_PRIVATE_IP_SCANNING: bool = False  # Strict defensive boundary

    # Security & Auth
    RATE_LIMIT_PER_MINUTE: int = 60
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"

    def get_safe_summary(self) -> dict[str, Any]:
        """Returns a sanitized configuration summary redacting secrets."""
        data = self.model_dump()
        sensitive_keys = {
            "APP_SECRET_KEY",
            "POSTGRES_PASSWORD",
            "DATABASE_URL",
            "DATABASE_SYNC_URL",
            "NEO4J_PASSWORD",
        }
        for key in sensitive_keys:
            if key in data and data[key]:
                data[key] = "******"
        return data


settings = Settings()
