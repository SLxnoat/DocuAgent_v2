"""Security utilities for SSRF mitigation, credential masking, and path validation."""

import re
import ipaddress
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.core.exceptions import DocuAgentException

# Regex pattern for secure path IDs (alphanumeric, dashes, underscores)
SAFE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

# Sensitive keyword patterns for input masking
SENSITIVE_FIELD_PATTERNS = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|auth|cvv|credit[_-]?card|ssn)",
    re.IGNORECASE,
)

# Cloud metadata and loopback IPs
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),          # Loopback
    ipaddress.ip_network("169.254.0.0/16"),        # Link-local / Cloud Metadata (AWS/GCP/Azure)
    ipaddress.ip_network("10.0.0.0/8"),           # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),        # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),       # RFC 1918 Private
    ipaddress.ip_network("::1/128"),              # IPv6 Loopback
    ipaddress.ip_network("fe80::/10"),            # IPv6 Link-local
]


class SecurityValidationError(DocuAgentException):
    """Raised when a security boundary is violated."""


def validate_target_url(url: str, allow_local: bool = True) -> str:
    """Validate URL scheme and protect against SSRF and unauthorized protocols."""
    if not url or not isinstance(url, str):
        raise SecurityValidationError("Invalid or empty URL.")

    parsed = urlparse(url.strip())
    
    # 1. Enforce HTTP/HTTPS only
    if parsed.scheme not in ("http", "https"):
        raise SecurityValidationError(f"Disallowed URL scheme: '{parsed.scheme}'. Only http and https are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SecurityValidationError("URL must include a valid hostname.")

    # 2. Block Cloud Metadata endpoints unconditionally
    if hostname in ("169.254.169.254", "metadata.google.internal", "instance-data"):
        raise SecurityValidationError("Access to cloud instance metadata services is strictly forbidden.")

    # 3. In strict production mode, check for private IP ranges if allow_local is False
    if settings.ENVIRONMENT == "production" and not allow_local:
        try:
            ip_obj = ipaddress.ip_address(hostname)
            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    raise SecurityValidationError(f"Targeting private IP space ({hostname}) is restricted.")
        except ValueError:
            # Hostname is a domain name, not a raw IP
            pass

    return url.strip()


def sanitize_identifier(identifier: str, field_name: str = "ID") -> str:
    """Validate identifier strings against path traversal characters."""
    if not identifier or not SAFE_ID_REGEX.match(identifier):
        raise SecurityValidationError(f"Invalid {field_name} format. Must contain only alphanumeric characters, underscores, or dashes.")
    return identifier


def mask_sensitive_value(field_name: Optional[str], input_type: Optional[str], value: Optional[str]) -> Optional[str]:
    """Mask password, secret, token, and credential values."""
    if value is None:
        return None

    if input_type and input_type.lower() == "password":
        return "••••••••"

    if field_name and SENSITIVE_FIELD_PATTERNS.search(field_name):
        return "••••••••"

    return value
