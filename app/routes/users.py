from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_user_by_email

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


@router.get("/by/email", response_model=UserResponse)
def get_user_by_email_route(
    email: EmailStr = Query(...), db: Session = Depends(get_db)
) -> UserResponse:
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
