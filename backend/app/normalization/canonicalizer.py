"""Canonical normalization routines for all supported entity types."""

import ipaddress
from typing import Any, Dict, Tuple
from urllib.parse import urlparse, urlunparse

import tldextract

from app.core.constants import EntityType


class Canonicalizer:
    """Provides deterministic value normalization across heterogeneous intelligence data."""

    @classmethod
    def canonicalize(cls, raw_value: str, entity_type: EntityType) -> Tuple[str, str, Dict[str, Any]]:
        """
        Returns: (normalized_value, display_value, metadata)
        - normalized_value: Deterministic lowercase/canonical string for unique indexing.
        - display_value: Human-readable display label.
        - metadata: Extracted structural properties (e.g., TLD, IP version).
        """
        val_clean = str(raw_value).strip()

        match entity_type:
            case EntityType.EMAIL:
                normalized = val_clean.lower()
                domain = normalized.split("@")[-1] if "@" in normalized else ""
                return normalized, val_clean, {"domain": domain}

            case EntityType.USERNAME:
                normalized = val_clean.lower()
                return normalized, val_clean, {"length": len(val_clean)}

            case EntityType.DOMAIN | EntityType.SUBDOMAIN:
                clean_host = val_clean.lower()
                if clean_host.startswith(("http://", "https://")):
                    clean_host = urlparse(clean_host).hostname or clean_host
                clean_host = clean_host.split("/")[0].split(":")[0].strip(".")

                extracted = tldextract.extract(clean_host)
                registered_domain = extracted.registered_domain
                is_subdomain = bool(extracted.subdomain)

                meta = {
                    "registered_domain": registered_domain,
                    "subdomain": extracted.subdomain,
                    "tld": extracted.suffix,
                    "is_subdomain": is_subdomain,
                }
                return clean_host, clean_host, meta

            case EntityType.IP:
                try:
                    ip_obj = ipaddress.ip_address(val_clean)
                    normalized = str(ip_obj)
                    return normalized, normalized, {
                        "version": ip_obj.version,
                        "is_private": ip_obj.is_private,
                        "is_global": ip_obj.is_global,
                    }
                except ValueError:
                    return val_clean.lower(), val_clean, {}

            case EntityType.URL:
                parsed = urlparse(val_clean)
                scheme = parsed.scheme.lower() or "http"
                netloc = (parsed.hostname or "").lower()
                if parsed.port and not ((scheme == "http" and parsed.port == 80) or (scheme == "https" and parsed.port == 443)):
                    netloc = f"{netloc}:{parsed.port}"
                path = parsed.path or "/"
                normalized = urlunparse((scheme, netloc, path, "", parsed.query, ""))
                return normalized, val_clean, {"hostname": parsed.hostname, "scheme": scheme}

            case EntityType.TECHNOLOGY:
                normalized = val_clean.lower().strip()
                return normalized, val_clean, {}

            case _:
                normalized = val_clean.lower()
                return normalized, val_clean, {}
