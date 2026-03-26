from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.task import Task
from app.models.team_members import TeamMember
from app.schemas.task import TaskCreate, TaskUpdate


def _get_task_or_raise(db: Session, task_id: UUID) -> Task:
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

    if not task:
        raise ValueError("No task with provided id.")

    return task


def _assert_user_in_team(db: Session, user_id: UUID, team_id: UUID) -> None:
    is_member = db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
    ).scalar_one_or_none()

    if not is_member:
        raise ValueError("User is not a member of this team.")


def _assert_team_in_project(db: Session, team_id: UUID, project_id: UUID) -> None:
    link = db.execute(
        select(ProjectTeam).where(
            ProjectTeam.team_id == team_id,
            ProjectTeam.project_id == project_id,
        )
    ).scalar_one_or_none()

    if not link:
        raise ValueError("Team is not assigned to this project.")


def get_tasks_for_project(
    db: Session, user_id: UUID, project_id: UUID, team_id: UUID
) -> list[Task]:
    _assert_user_in_team(db, user_id, team_id)
    _assert_team_in_project(db, team_id, project_id)

    result = db.execute(
        select(Task).where(Task.project_id == project_id, Task.team_id == team_id)
    )
    return result.scalars().all()


def get_task_by_id(db: Session, user_id: UUID, task_id: UUID) -> Task:
    task = _get_task_or_raise(db, task_id)
    _assert_user_in_team(db, user_id, task.team_id)
    return task


def create_task(db: Session, creator_id: UUID, data: TaskCreate) -> Task:
    _assert_user_in_team(db, creator_id, data.team_id)
    _assert_team_in_project(db, data.team_id, data.project_id)

    new_task = Task(
        title=data.title,
        description=data.description,
        project_id=data.project_id,
        team_id=data.team_id,
        creator_id=creator_id,
        assignee_id=data.assignee_id,
    )
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Task not created.") from e


def edit_task(db: Session, user_id: UUID, task_id: UUID, data: TaskUpdate) -> Task:
    task = _get_task_or_raise(db, task_id)
    _assert_user_in_team(db, user_id, task.team_id)

    updates = {
        "title": data.title,
        "description": data.description,
        "assignee_id": data.assignee_id,
        "status_id": data.status_id,
    }
    for field, value in updates.items():
        if value is not None:
            setattr(task, field, value)

    try:
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Task not updated.") from e


def delete_task(db: Session, user_id: UUID, task_id: UUID) -> Task:
    task = _get_task_or_raise(db, task_id)

    project = db.execute(
        select(Project).where(Project.id == task.project_id)
    ).scalar_one_or_none()

    if not project:
        raise ValueError("Project not found.")

    is_member = db.execute(
        select(ProjectTeam)
        .join(TeamMember, ProjectTeam.team_id == TeamMember.team_id)
        .where(
            ProjectTeam.project_id == task.project_id,
            TeamMember.user_id == user_id,
        )
    ).scalar_one_or_none()

    if not is_member:
        raise ValueError("Only a team member of this project can delete tasks.")

    try:
        db.delete(task)
        db.commit()
        return task
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Task not deleted.") from e
