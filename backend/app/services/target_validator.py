"""Target validation service with defensive checks, RFC validation, and private network protection."""

import ipaddress
import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import tldextract
from email_validator import EmailNotValidError, validate_email as rfc_validate_email

from app.core.config import settings
from app.core.constants import TargetType
from app.core.exceptions import TargetValidationError


class TargetValidator:
    """Validates, canonicalizes, and performs safety screening on candidate targets."""

    USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{2,64}$")
    DOMAIN_REGEX = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    )

    @classmethod
    def validate(
        cls,
        target_input: str,
        target_type: TargetType,
        allow_private_ip: Optional[bool] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Validates target syntax and safety. Returns canonical target and parsed metadata.
        Raises TargetValidationError on invalid input or safety violations.
        """
        if not target_input or not isinstance(target_input, str):
            raise TargetValidationError("Target input must be a non-empty string.")

        target_clean = target_input.strip()
        if not target_clean:
            raise TargetValidationError("Target cannot be whitespace-only.")

        if allow_private_ip is None:
            allow_private_ip = settings.ALLOW_PRIVATE_IP_SCANNING

        match target_type:
            case TargetType.EMAIL:
                return cls._validate_email(target_clean)
            case TargetType.USERNAME:
                return cls._validate_username(target_clean)
            case TargetType.DOMAIN:
                return cls._validate_domain(target_clean)
            case TargetType.IP:
                return cls._validate_ip(target_clean, allow_private_ip)
            case TargetType.URL:
                return cls._validate_url(target_clean, allow_private_ip)
            case _:
                raise TargetValidationError(f"Unsupported target type: {target_type}")

    @classmethod
    def _validate_email(cls, email: str) -> Tuple[str, Dict[str, Any]]:
        try:
            valid_info = rfc_validate_email(email, check_deliverability=False)
            normalized = valid_info.normalized.lower()
            return normalized, {
                "local_part": valid_info.local_part.lower(),
                "domain": valid_info.domain.lower(),
                "ascii_email": valid_info.ascii_email.lower(),
            }
        except EmailNotValidError as exc:
            raise TargetValidationError(f"Invalid email syntax: {str(exc)}") from exc

    @classmethod
    def _validate_username(cls, username: str) -> Tuple[str, Dict[str, Any]]:
        if not cls.USERNAME_REGEX.match(username):
            raise TargetValidationError(
                f"Invalid username '{username}'. Usernames must be 2–64 alphanumeric characters, dots, dashes, or underscores."
            )
        normalized = username.strip()
        return normalized, {"length": len(normalized)}

    @classmethod
    def _validate_domain(cls, domain: str) -> Tuple[str, Dict[str, Any]]:
        # Strip protocols or paths if pasted accidentally
        clean_domain = domain.lower()
        if clean_domain.startswith(("http://", "https://")):
            clean_domain = urlparse(clean_domain).hostname or clean_domain
        clean_domain = clean_domain.split("/")[0].split(":")[0].strip(".")

        if not cls.DOMAIN_REGEX.match(clean_domain):
            raise TargetValidationError(f"Invalid domain format: '{domain}'")

        extracted = tldextract.extract(clean_domain)
        if not extracted.suffix:
            raise TargetValidationError(f"Domain '{domain}' does not have a recognized public suffix (TLD).")

        registered_domain = extracted.registered_domain
        return clean_domain, {
            "subdomain": extracted.subdomain,
            "domain": extracted.domain,
            "suffix": extracted.suffix,
            "registered_domain": registered_domain,
            "is_subdomain": bool(extracted.subdomain),
        }

    @classmethod
    def _validate_ip(cls, ip_str: str, allow_private: bool) -> Tuple[str, Dict[str, Any]]:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError as exc:
            raise TargetValidationError(f"Invalid IP address format: '{ip_str}'") from exc

        is_private = ip_obj.is_private
        is_loopback = ip_obj.is_loopback
        is_multicast = ip_obj.is_multicast
        is_reserved = ip_obj.is_reserved

        if not allow_private and (is_private or is_loopback or is_multicast or is_reserved):
            raise TargetValidationError(
                f"IP address '{ip_str}' is a private, loopback, or reserved address. Active scanning of internal networks is restricted."
            )

        return str(ip_obj), {
            "version": ip_obj.version,
            "is_private": is_private,
            "is_loopback": is_loopback,
            "is_global": ip_obj.is_global,
            "compressed": ip_obj.compressed,
        }

    @classmethod
    def _validate_url(cls, url_str: str, allow_private: bool) -> Tuple[str, Dict[str, Any]]:
        parsed = urlparse(url_str)
        if parsed.scheme not in ("http", "https"):
            raise TargetValidationError("URL must begin with http:// or https://")

        hostname = parsed.hostname
        if not hostname:
            raise TargetValidationError(f"Invalid URL host in '{url_str}'")

        # Check if host is an IP
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if not allow_private and (ip_obj.is_private or ip_obj.is_loopback):
                raise TargetValidationError(f"URL points to a private/loopback IP: '{hostname}'")
        except ValueError:
            # It is a domain/hostname
            pass

        canonical_url = parsed.geturl()
        return canonical_url, {
            "scheme": parsed.scheme,
            "hostname": hostname,
            "port": parsed.port or (443 if parsed.scheme == "https" else 80),
            "path": parsed.path or "/",
        }
