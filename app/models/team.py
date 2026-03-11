from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
  from app.models.team_members import TeamMember
  

class Team(Base):
  __tablename__="teams"
  
  id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
  
  user_links: Mapped[list["TeamMember"]] = relationship(
    "TeamMember",
    back_populates="team",
    cascade="all, delete-orphan"
  )