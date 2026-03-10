from uuid import uuid4, UUID
from sqlalchemy import String, Boolean, Date, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class User(Base):
  __tablename__="users"

  id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  surname: Mapped[str] = mapped_column(String(255), nullable=False)
  email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  created_at: Mapped[Date] = mapped_column(Date, nullable=False, default=func.now())
  updated_at: Mapped[Date] = mapped_column(Date, nullable=False, default=func.now(), onupdate=func.now())