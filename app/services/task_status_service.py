from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_status import TaskStatus


def get_all_statuses(db: Session) -> list[TaskStatus]:
    result = db.execute(select(TaskStatus))
    return result.scalars().all()


def get_status_by_id(db: Session, status_id: UUID) -> TaskStatus:
    status = db.execute(
        select(TaskStatus).where(TaskStatus.id == status_id)
    ).scalar_one_or_none()

    if not status:
        raise ValueError("No status with provided id.")

    return status
