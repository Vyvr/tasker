from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.team import Team
    from app.models.user import User
    from app.models.task_status import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        index=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(3000), nullable=True)
    creator_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    assignee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    status_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_statuses.id", ondelete="SET NULL"),
        nullable=False,
        server_default=text("'00000000-0000-0000-0000-000000000001'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[creator_id],
    )
    assignee: Mapped["User"] = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
    )
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="tasks",
    )
    assigned_status: Mapped["TaskStatus"] = relationship(
        "TaskStatus", foreign_keys=[status_id], viewonly=True
    )
