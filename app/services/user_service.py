from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.hasher import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserDelete


def get_user_by_email(db: Session, email: str) -> User | None:
    query = select(User).where(User.email == email.lower())
    result = db.execute(query)
    user = result.scalar_one_or_none()
    return user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    query = select(User).where(User.id == user_id)
    result = db.execute(query)
    return result.scalar_one_or_none()


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_email(db, user.email.lower())
    if existing_user:
        raise ValueError("User with this email already exists")

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        surname=user.surname,
        email=user.email.lower(),
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def delete_user(db: Session, user_id: UUID) -> UserDelete:
    user_for_deletion = get_user_by_id(db, user_id)

    if not user_for_deletion:
        raise ValueError("No user with provided id.")

    deleted_id = user_for_deletion.id

    try:
        db.delete(user_for_deletion)
        db.commit()
        return UserDelete(
            id=deleted_id,
            message="User deleted successfully.",
        )
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. User not deleted.") from e


def edit_user(
    user_id: UUID,
    new_name: str | None,
    new_surname: str | None,
    new_email: str | None,
    current_user_id: UUID,
    db: Session,
) -> User:
    if user_id != current_user_id:
        raise ValueError("You can't edit other users except yourself.")

    user_to_edit = get_user_by_id(db, user_id)

    if not user_to_edit:
        raise ValueError("User with provided id doesn't exist.")

    updates = {
        "name": new_name,
        "surname": new_surname,
        "email": new_email,
    }
    for field, value in updates.items():
        if value is not None:
            setattr(user_to_edit, field, value)

    try:
        db.commit()
        db.refresh(user_to_edit)
        return user_to_edit
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. User not updated.") from e


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(db, email.lower())

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
