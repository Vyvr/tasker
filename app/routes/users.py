from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.auth import create_access_token
from app.core.config import ENVIRONMENT
from app.models.user import User
from app.schemas.user import LoginResponse, UserCreate, UserLoginRequest, UserResponse
from app.services.user_service import authenticate_user, create_user, get_user_by_email, get_user_by_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
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
    user = authenticate_user(db, user_in.email, user_in.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    access_token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=ENVIRONMENT != "dev",
        samesite="lax",
        max_age=60 * 10,
    )

    return LoginResponse(message="Login successful.")


@router.post("/logout", response_model=LoginResponse)
def logout_user_route(response: Response) -> LoginResponse:
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=ENVIRONMENT != "dev",
        samesite="lax",
    )
    return LoginResponse(message="Logout successful")


@router.get("/me", response_model=UserResponse)
def get_me_route(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user


@router.get("/by/email", response_model=UserResponse)
def get_user_by_email_route(
    email: EmailStr = Query(...),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get("/by/id/{user_id}", response_model=UserResponse)
def get_user_by_id_route(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user: User = Depends(get_current_user),
) -> UserResponse:
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
