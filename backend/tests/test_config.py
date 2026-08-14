"""Tests for configuration settings and secret sanitization."""

from app.core.config import Settings


def test_default_settings():
    """Verify default setting initialization."""
    config = Settings()
    assert config.APP_NAME == "OSINT-X"
    assert config.POSTGRES_PORT == 5432
    assert config.RATE_LIMIT_PER_MINUTE == 60
    assert config.COLLECTOR_TIMEOUT_SECONDS == 180
    assert config.ENABLE_STRICT_TARGET_VALIDATION is True
    assert config.ALLOW_PRIVATE_IP_SCANNING is False


def test_cors_origins_parsing():
    """Verify string list and JSON array parsing for CORS origins."""
    config1 = Settings(CORS_ORIGINS="http://test.com, http://example.com")
    assert "http://test.com" in config1.CORS_ORIGINS
    assert "http://example.com" in config1.CORS_ORIGINS

    config2 = Settings(CORS_ORIGINS='["http://sub.domain.org"]')
    assert config2.CORS_ORIGINS == ["http://sub.domain.org"]


def test_secret_sanitization_summary():
    """Verify secrets are redacted in safe summary output."""
    config = Settings(
        APP_SECRET_KEY="super-secret-key-12345",
        POSTGRES_PASSWORD="my_db_password",
        NEO4J_PASSWORD="my_neo4j_password",
    )
    safe = config.get_safe_summary()
    assert safe["APP_SECRET_KEY"] == "******"
    assert safe["POSTGRES_PASSWORD"] == "******"
    assert safe["NEO4J_PASSWORD"] == "******"
    assert safe["DATABASE_URL"] == "******"
    assert safe["APP_NAME"] == "OSINT-X"
