"""
app/core/security.py
--------------------
JWT creation & verification helpers.

Phase 1 only provides the token-verification skeleton needed by the
dependency injection layer.  Full authentication logic will be completed
in Phase 2 (Auth service).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Token creation (used by tests / admin utilities)
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


# ------------------------------------------------------------------ #
# Token verification
# ------------------------------------------------------------------ #

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.

    Raises:
        jwt.ExpiredSignatureError: Token has expired.
        jwt.InvalidTokenError: Token is malformed or signature invalid.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


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
