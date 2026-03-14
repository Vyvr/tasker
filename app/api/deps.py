from collections.abc import Generator
from uuid import UUID
from fastapi import Depends, HTTPException, Header, Request, status
import jwt
from sqlalchemy.orm import Session

from app.core.auth import decode_token, verify_csrf_token
from app.db.session import SessionLocal
from app.models.user import User
from app.services.user_service import get_user_by_id


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )

        user = get_user_by_id(db, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


def validate_csrf_for_refresh(
    request: Request,
    x_csrf_token: str = Header(..., alias="X-CSRF-Token"),
) -> None:
    csrf_token = request.cookies.get("csrf_token")
    csrf_signature = request.cookies.get("csrf_signature")
    refresh_token = request.cookies.get("refresh_token")

    if not csrf_token or not csrf_signature or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing CSRF protection",
        )

    if x_csrf_token != csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )

    if not verify_csrf_token(csrf_token, csrf_signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF signature",
        )


def validate_csrf(
    request: Request,
    x_csrf_token: str = Header(..., alias="X-CSRF-Token"),
) -> None:
    csrf_token = request.cookies.get("csrf_token")
    csrf_signature = request.cookies.get("csrf_signature")

    if not csrf_token or not csrf_signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing CSRF protection",
        )

    if x_csrf_token != csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )

    if not verify_csrf_token(csrf_token, csrf_signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF signature",
        )

