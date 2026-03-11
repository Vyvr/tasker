from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.hasher import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> User:
  query = select(User).where(User.email == email)
  result = db.execute(query)
  user = result.scalar_one_or_none()
  print("existing_user: ", user)
  return user

def create_user(db: Session, user: UserCreate) -> User:
  existing_user = get_user_by_email(db, user.email)
  if existing_user:
    raise ValueError("User with this email already exists")
  
  hashed_password = hash_password(user.password)
  
  new_user = User(
    name=user.name,
    surname=user.surname,
    email=user.email,
    password=hashed_password
  )
  
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  
  return new_user