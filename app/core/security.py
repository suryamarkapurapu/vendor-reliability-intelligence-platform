"""
Password hashing and verification security utilities using Passlib and bcrypt.
"""

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)


get_password_hash = hash_password



def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """
    try:
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )
    except (ValueError, TypeError, UnknownHashError):
        return False