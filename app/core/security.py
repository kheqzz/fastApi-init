import datetime
from typing import Optional

from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def get_password_verify(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(password, hashed_password)


def create_access_token(
    *,
    secrets: dict,
    expiration_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
) -> str:
    """
    Create a JWT token.

    Args:
        secrets: Dictionary containing at least ``secret`` and ``algorithm`` keys.
        expiration_minutes: Token expiration in minutes (default reads from settings).

    Returns:
        A signed JWT string.
    """
    payload = {
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(minutes=expiration_minutes)
        | datetime.timezone.utc,
    }
    payload.update(secrets)
    # Import jwt only when needed to avoid hard dependency unless used
    import jwt  # type: ignore

    return jwt.encode(payload, secrets["secret"], algorithm=secrets["algorithm"])


def decode_access_token(token: str, secrets: dict) -> dict:
    """
    Decode a JWT token and return its payload.

    Args:
        token: JWT string.
        secrets: Same dictionary used for signing.

    Returns:
        Payload dictionary.

    Raises:
        jwt.exceptions.InvalidTokenError: If token is invalid or expired.
    """
    import jwt  # type: ignore
    return jwt.decode(token, secrets["secret"], algorithms=[secrets["algorithm"]])


class AuthError(Exception):
    """Base class for authentication-related errors."""

    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.status_code = status_code