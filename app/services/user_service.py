from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.hasher import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = db.execute(query)
    user = result.scalar_one_or_none()
    print("existing_user: ", user)
    return user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    query = select(User).where(User.id == user_id)
    result = db.execute(query)
    return result.scalar_one_or_none()


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("User with this email already exists")

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name, surname=user.surname, email=user.email, password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
  user = get_user_by_email(db, email)
  
  if not user:
    return None
  
  if not verify_password(password, user.password):
    return None
  
  return user