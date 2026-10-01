"""
JWT Security Utilities for Authentication and Token Management.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Creates a signed JWT access token with an expiration time.

    Args:
        data: Payload dictionary to encode into the token.
        expires_delta: Optional custom token expiration duration.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(
    token: str,
) -> dict:
    """
    Decodes and verifies a JWT access token.

    Args:
        token: Signed JWT token string.

    Returns:
        Decoded payload dictionary.

    Raises:
        JWTError: If token signature, expiration, or format is invalid.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    return payload


def get_current_user_id(
    token: str,
) -> UUID:
    """
    Decodes a JWT access token and extracts the authenticated user's UUID from 'sub' claim.

    Args:
        token: Signed JWT token string.

    Returns:
        UUID of the user contained in the 'sub' claim.

    Raises:
        JWTError: If token is invalid or 'sub' claim is missing or not a valid UUID.
    """
    payload = decode_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise JWTError("Token payload missing subject ('sub') claim.")

    try:
        return UUID(str(user_id_str))
    except (ValueError, TypeError) as exc:
        raise JWTError("Invalid UUID format in token subject ('sub') claim.") from exc
