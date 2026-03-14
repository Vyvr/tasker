from datetime import datetime, timedelta
import hashlib
import hmac
from uuid import UUID
import jwt
import secrets
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    CSRF_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


def create_access_token(user_id: UUID) -> str:
    now = datetime.now()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["exp", "sub", "type"]},
    )


def create_refresh_token(user_id: UUID) -> str:
    now = datetime.now()
    expire = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def sign_csrf_token(csrf_token: str) -> str:
    message = f"{csrf_token}".encode()
    return hmac.new(
        CSRF_SECRET_KEY.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_csrf_token(csrf_token: str, csrf_signature: str) -> bool:
    expected = sign_csrf_token(csrf_token)
    return hmac.compare_digest(expected, csrf_signature)
