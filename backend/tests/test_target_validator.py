"""Tests for TargetValidator across email, username, domain, IP, and URL types."""

import pytest
from app.core.constants import TargetType
from app.core.exceptions import TargetValidationError
from app.services.target_validator import TargetValidator


def test_validate_email_valid():
    """Test valid email inputs and normalization."""
    canonical, meta = TargetValidator.validate("  User.Test@Example.COM  ", TargetType.EMAIL)
    assert canonical == "user.test@example.com"
    assert meta["domain"] == "example.com"
    assert meta["local_part"] == "user.test"


def test_validate_email_invalid():
    """Test invalid email inputs."""
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("plainaddress", TargetType.EMAIL)
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("@missinglocal.com", TargetType.EMAIL)


def test_validate_username_valid():
    """Test valid usernames."""
    canonical, meta = TargetValidator.validate("cyber_analyst-01", TargetType.USERNAME)
    assert canonical == "cyber_analyst-01"
    assert meta["length"] == 16


def test_validate_username_invalid():
    """Test invalid usernames with forbidden chars or illegal lengths."""
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("a", TargetType.USERNAME)  # < 2 chars
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("bad username with spaces", TargetType.USERNAME)
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("user;rm -rf /", TargetType.USERNAME)


def test_validate_domain_valid():
    """Test domain normalization and TLD extraction."""
    canonical, meta = TargetValidator.validate("HTTPS://Sub.Target.CO.UK/path", TargetType.DOMAIN)
    assert canonical == "sub.target.co.uk"
    assert meta["registered_domain"] == "target.co.uk"
    assert meta["suffix"] == "co.uk"
    assert meta["is_subdomain"] is True


def test_validate_domain_invalid():
    """Test invalid domain syntax or invalid TLD."""
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("invalid_domain..com", TargetType.DOMAIN)
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("localhost", TargetType.DOMAIN)


def test_validate_ip_public():
    """Test public IPv4/IPv6 validation."""
    canonical, meta = TargetValidator.validate("8.8.8.8", TargetType.IP, allow_private_ip=False)
    assert canonical == "8.8.8.8"
    assert meta["is_global"] is True
    assert meta["is_private"] is False


def test_validate_ip_private_blocked():
    """Verify private/loopback IP is blocked by default."""
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("127.0.0.1", TargetType.IP, allow_private_ip=False)
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("192.168.1.1", TargetType.IP, allow_private_ip=False)
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("10.0.0.5", TargetType.IP, allow_private_ip=False)


def test_validate_ip_private_allowed_when_flagged():
    """Verify private IP is allowed when explicit lab flag is enabled."""
    canonical, meta = TargetValidator.validate("192.168.1.50", TargetType.IP, allow_private_ip=True)
    assert canonical == "192.168.1.50"
    assert meta["is_private"] is True


def test_validate_url_valid():
    """Test valid HTTP/HTTPS URLs."""
    canonical, meta = TargetValidator.validate("https://api.target.com/v1/status", TargetType.URL)
    assert canonical == "https://api.target.com/v1/status"
    assert meta["hostname"] == "api.target.com"
    assert meta["port"] == 443
    assert meta["scheme"] == "https"


def test_validate_url_invalid():
    """Test invalid URL schemes (ftp/file/gopher)."""
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("ftp://target.com/file", TargetType.URL)
    with pytest.raises(TargetValidationError):
        TargetValidator.validate("not-a-url", TargetType.URL)
