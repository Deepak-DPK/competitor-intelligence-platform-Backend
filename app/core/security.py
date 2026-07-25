"""
app/core/security.py
--------------------
JWT creation & verification helpers + password hashing.

Phase 3 adds:
- bcrypt password hashing via passlib
- create_refresh_token()
- Token-type discrimination (access vs. refresh)
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# Password hashing context (bcrypt)
# ------------------------------------------------------------------ #

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


# ------------------------------------------------------------------ #
# Token creation
# ------------------------------------------------------------------ #

def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The token subject (typically user UUID).
        expires_delta: Override the default expiry window.
        additional_claims: Extra key-value pairs merged into the payload.

    Returns:
        Signed JWT string.
    """
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(tz=timezone.utc),
        "type": "access",
    }
    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT refresh token (longer-lived than access tokens).

    Refresh tokens carry ``type: refresh`` so the verify step can
    discriminate between token types and reject access tokens presented
    at the refresh endpoint (and vice-versa).
    """
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(days=30)
    )
    payload: dict = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(tz=timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ------------------------------------------------------------------ #
# Token verification
# ------------------------------------------------------------------ #

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Raises:
        jwt.ExpiredSignatureError: Token has expired.
        jwt.InvalidTokenError:    Token is malformed or wrong type.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "access":
        raise InvalidTokenError("Not an access token")
    return payload


def decode_refresh_token(token: str) -> dict:
    """
    Decode and verify a JWT refresh token.

    Raises:
        jwt.ExpiredSignatureError: Token has expired.
        jwt.InvalidTokenError:    Token is malformed or wrong type.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Not a refresh token")
    return payload


def verify_supabase_jwt(token: str) -> dict:
    """
    Verify a JWT issued by Supabase using the project's JWT secret.

    Returns the decoded payload on success; raises on failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},  # Supabase does not set aud by default
        )
        return payload
    except ExpiredSignatureError:
        logger.warning("Supabase JWT has expired")
        raise
    except (DecodeError, InvalidTokenError) as exc:
        logger.warning("Supabase JWT verification failed: %s", exc)
        raise
