"""
TitanForge Security Hardening Module
Rate limiting, CSRF tokens, security headers, input sanitization.

Protections included:
  1. Rate limiting (login + API endpoints)
  2. CSRF token generation and validation
  3. Security headers (CSP, X-Frame-Options, HSTS, etc.)
  4. Input sanitization (XSS prevention)
  5. Session security (HttpOnly, SameSite cookies)
  6. IP-based brute force detection
"""

from __future__ import annotations
import os
import re
import time
import html
import secrets
import hashlib
import json
from collections import defaultdict
from typing import Optional, Dict, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMITER — In-memory sliding window
# ─────────────────────────────────────────────────────────────────────────────

class RateLimiter:
    """
    Sliding window rate limiter keyed by IP address.
    Tracks request timestamps per key and enforces max requests per window.
    """

    def __init__(self):
        # key -> list of timestamps
        self._requests: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # cleanup every 5 minutes

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        Returns (allowed: bool, remaining: int).
        """
        now = time.time()
        cutoff = now - window_seconds

        # Periodic cleanup of stale entries
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup(cutoff)

        # Remove timestamps outside the window
        timestamps = self._requests[key]
        timestamps[:] = [t for t in timestamps if t > cutoff]

        if len(timestamps) >= max_requests:
            return False, 0

        timestamps.append(now)
        remaining = max_requests - len(timestamps)
        return True, remaining

    def _cleanup(self, cutoff: float):
        """Remove stale entries to prevent memory growth."""
        stale_keys = []
        for key, timestamps in self._requests.items():
            timestamps[:] = [t for t in timestamps if t > cutoff]
            if not timestamps:
                stale_keys.append(key)
        for k in stale_keys:
            del self._requests[k]
        self._last_cleanup = time.time()

    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests without consuming one."""
        now = time.time()
        cutoff = now - window_seconds
        timestamps = [t for t in self._requests.get(key, []) if t > cutoff]
        return max(0, max_requests - len(timestamps))


# Global rate limiters
LOGIN_LIMITER = RateLimiter()
API_LIMITER = RateLimiter()
REGISTER_LIMITER = RateLimiter()

# Rate limit configs
LOGIN_RATE = (10, 300)      # 10 attempts per 5 minutes per IP
API_RATE = (120, 60)        # 120 requests per minute per IP
REGISTER_RATE = (3, 3600)   # 3 registrations per hour per IP


def check_login_rate(ip: str) -> Tuple[bool, int]:
    """Check if login attempt is within rate limit."""
    return LOGIN_LIMITER.is_allowed(f"login:{ip}", *LOGIN_RATE)


def check_api_rate(ip: str) -> Tuple[bool, int]:
    """Check if API request is within rate limit."""
    return API_LIMITER.is_allowed(f"api:{ip}", *API_RATE)


def check_register_rate(ip: str) -> Tuple[bool, int]:
    """Check if registration is within rate limit."""
    return REGISTER_LIMITER.is_allowed(f"reg:{ip}", *REGISTER_RATE)


# ─────────────────────────────────────────────────────────────────────────────
# CSRF PROTECTION
# ─────────────────────────────────────────────────────────────────────────────

def generate_csrf_token() -> str:
    """Generate a random CSRF token."""
    return secrets.token_hex(32)


def validate_csrf_token(session_token: str, submitted_token: str) -> bool:
    """Validate CSRF token using constant-time comparison."""
    if not session_token or not submitted_token:
        return False
    return secrets.compare_digest(session_token, submitted_token)


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY HEADERS
# ─────────────────────────────────────────────────────────────────────────────

SECURITY_HEADERS = {
    # Prevent clickjacking
    "X-Frame-Options": "SAMEORIGIN",
    # Prevent MIME type sniffing
    "X-Content-Type-Options": "nosniff",
    # XSS protection (legacy browsers)
    "X-XSS-Protection": "1; mode=block",
    # Referrer policy — don't leak URLs to external sites
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Permissions policy — disable unnecessary browser features
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    # Content Security Policy — prevent XSS and injection
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'self'; "
        "base-uri 'self'; "
        "form-action 'self';"
    ),
    # Cache control for authenticated pages
    "Cache-Control": "no-store, no-cache, must-revalidate, private",
    "Pragma": "no-cache",
}


def apply_security_headers(handler):
    """Apply all security headers to a Tornado handler response."""
    for header, value in SECURITY_HEADERS.items():
        handler.set_header(header, value)


# ─────────────────────────────────────────────────────────────────────────────
# INPUT SANITIZATION
# ─────────────────────────────────────────────────────────────────────────────

# Pattern to detect common XSS vectors
XSS_PATTERNS = [
    re.compile(r'<script[^>]*>', re.IGNORECASE),
    re.compile(r'javascript\s*:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick=, onerror=, etc.
    re.compile(r'<iframe[^>]*>', re.IGNORECASE),
    re.compile(r'<object[^>]*>', re.IGNORECASE),
    re.compile(r'<embed[^>]*>', re.IGNORECASE),
    re.compile(r'<form[^>]*>', re.IGNORECASE),
    re.compile(r'expression\s*\(', re.IGNORECASE),  # CSS expression
    re.compile(r'url\s*\(\s*["\']?\s*javascript', re.IGNORECASE),
]


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string input:
    - HTML-encode special characters
    - Truncate to max length
    - Strip null bytes
    """
    if not isinstance(value, str):
        return ""
    # Remove null bytes
    value = value.replace('\x00', '')
    # Truncate
    value = value[:max_length]
    # HTML-encode dangerous characters
    value = html.escape(value, quote=True)
    return value.strip()


def sanitize_username(username: str) -> str:
    """Sanitize username: lowercase, alphanumeric + underscores only."""
    if not isinstance(username, str):
        return ""
    # Strip, lowercase, remove anything that's not alphanumeric or underscore
    cleaned = re.sub(r'[^a-z0-9_]', '', username.strip().lower())
    return cleaned[:50]  # max 50 chars


def sanitize_email(email: str) -> str:
    """Basic email sanitization and validation."""
    if not isinstance(email, str):
        return ""
    email = email.strip().lower()[:254]
    # Basic email pattern
    if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
        return ""
    return email


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number: keep digits, +, -, (, ), spaces."""
    if not isinstance(phone, str):
        return ""
    cleaned = re.sub(r'[^\d+\-() ]', '', phone.strip())
    return cleaned[:20]


def has_xss_patterns(value: str) -> bool:
    """Check if a string contains potential XSS patterns."""
    if not value:
        return False
    for pattern in XSS_PATTERNS:
        if pattern.search(value):
            return True
    return False


def sanitize_dict(data: dict, allowed_keys: set = None) -> dict:
    """
    Sanitize all string values in a dictionary.
    Optionally restrict to allowed keys only.
    """
    result = {}
    for key, value in data.items():
        if allowed_keys and key not in allowed_keys:
            continue
        if isinstance(value, str):
            result[key] = sanitize_string(value)
        elif isinstance(value, list):
            result[key] = [sanitize_string(v) if isinstance(v, str) else v for v in value]
        else:
            result[key] = value
    return result


# ─────────────────────────────────────────────────────────────────────────────
# PASSWORD STRENGTH VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets minimum security requirements.
    Returns (valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 128:
        return False, "Password must be 128 characters or fewer"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# SESSION SECURITY
# ─────────────────────────────────────────────────────────────────────────────

# Secure cookie settings for Tornado
SECURE_COOKIE_KWARGS = {
    "httponly": True,
    "samesite": "Lax",
    # "secure": True,  # Enable this when using HTTPS
}
