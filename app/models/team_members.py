from typing import TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
  from app.models.team import Team
  from app.models.user import User

class TeamMember(Base):
  __tablename__ = "team_members"
  
  user_id: Mapped[UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    primary_key=True
  )
  team_id: Mapped[UUID] = mapped_column(
    ForeignKey("teams.id", ondelete="CASCADE"),
    primary_key=True
  )
  joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
  
  user: Mapped["User"] = relationship("User", back_populates="team_links")
  team: Mapped["Team"] = relationship("Team", back_populates="user_links")