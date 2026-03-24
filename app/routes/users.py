from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import (
    authenticate,
    get_db,
    validate_csrf,
)
from app.core.auth import (
    create_access_token,
    create_csrf_token,
    create_refresh_token,
    decode_token,
    sign_csrf_token,
)
from app.core.config import ENVIRONMENT
from app.models.user import User
from app.schemas.user import (
    LoginResponse,
    MinimalUserResponse,
    RefreshResponse,
    UserCreate,
    UserDelete,
    UserLoginRequest,
    UserResponse,
)
from app.services.user_service import (
    authenticate_user,
    create_user,
    delete_user,
    edit_user,
    get_user_by_email,
    get_user_by_id,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        user = create_user(db, user)
        return user
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/login", response_model=LoginResponse)
def login_user_route(
    user_in: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    user = authenticate_user(db, user_in.email.lower(), user_in.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    csrf_token = create_csrf_token()
    csrf_signature = sign_csrf_token(csrf_token)

    secure_cookie = ENVIRONMENT != "dev"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=60 * 10,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/users/refresh",
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=secure_cookie,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    response.set_cookie(
        key="csrf_signature",
        value=csrf_signature,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    user.last_login_at = datetime.now()
    user.is_online = True
    db.commit()
    db.refresh(user)

    return LoginResponse(message="Login successful.")


@router.post("/refresh", response_model=RefreshResponse)
def refresh_token_route(
    request: Request,
    response: Response,
) -> RefreshResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    try:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        new_access_token = create_access_token(UUID(user_id))
        new_refresh_token = create_refresh_token(UUID(user_id))

        new_csrf_token = create_csrf_token()
        new_csrf_signature = sign_csrf_token(new_csrf_token)

        secure_cookie = ENVIRONMENT != "dev"

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=secure_cookie,
            samesite="lax",
            max_age=60 * 10,
            path="/",
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
            path="/users/refresh",
        )
        response.set_cookie(
            key="csrf_token",
            value=new_csrf_token,
            httponly=False,
            secure=secure_cookie,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
            path="/",
        )
        response.set_cookie(
            key="csrf_signature",
            value=new_csrf_signature,
            httponly=True,
            secure=secure_cookie,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
            path="/",
        )

        return RefreshResponse(message="Token refreshed")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout", response_model=LoginResponse)
def logout_user_route(
    response: Response,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> LoginResponse:
    secure_cookie = ENVIRONMENT != "dev"

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        path="/users/refresh",
    )
    response.delete_cookie(
        key="csrf_token",
        httponly=False,
        secure=secure_cookie,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="csrf_signature",
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        path="/",
    )

    current_user.is_online = False
    db.commit()
    db.refresh(current_user)

    return LoginResponse(message="Logout successful")


@router.get("/me", response_model=UserResponse)
def get_me_route(
    current_user: User = Depends(authenticate),
) -> UserResponse:
    return current_user


@router.get("/find_by/email", response_model=UserResponse)
def get_user_by_email_route(
    email: EmailStr = Query(...),
    db: Session = Depends(get_db),
    _: None = Depends(authenticate),
) -> UserResponse:
    user = get_user_by_email(db, email.lower())

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get(
    "/find_by/id/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def get_user_by_id_route(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(authenticate),
) -> UserResponse:
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/delete", response_model=UserDelete)
def delete_user_route(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: None = Depends(authenticate),
    __: None = Depends(validate_csrf),
) -> UserDelete:
    try:
        user_for_deletion = delete_user(db, user_id)
        return user_for_deletion
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )


@router.put(
    "/{user_id}",
    response_model=MinimalUserResponse,
    status_code=status.HTTP_200_OK,
)
def edit_user_route(
    user_id: UUID,
    name: str | None = None,
    surname: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate),
    _: None = Depends(validate_csrf),
) -> MinimalUserResponse:
    try:
        edited_user = edit_user(user_id, name, surname, email, current_user.id, db)
        return edited_user
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )
