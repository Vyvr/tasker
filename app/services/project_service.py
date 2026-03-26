from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.team_members import TeamMember
from app.schemas.project import ProjectCreate, ProjectUpdate


def _get_project_or_raise(db: Session, project_id: UUID) -> Project:
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalar_one_or_none()

    if not project:
        raise ValueError("No project with provided id.")

    return project


def _assert_user_in_project(db: Session, user_id: UUID, project_id: UUID) -> None:
    is_member = db.execute(
        select(ProjectTeam)
        .join(TeamMember, ProjectTeam.team_id == TeamMember.team_id)
        .where(
            ProjectTeam.project_id == project_id,
            TeamMember.user_id == user_id,
        )
    ).scalar_one_or_none()

    if not is_member:
        raise ValueError("User is not a member of this project.")


def _assert_user_in_team(db: Session, user_id: UUID, team_id: UUID) -> None:
    is_member = db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
    ).scalar_one_or_none()

    if not is_member:
        raise ValueError("User is not a member of this team.")


def get_projects_for_team(db: Session, user_id: UUID, team_id: UUID) -> list[Project]:
    _assert_user_in_team(db, user_id, team_id)

    result = db.execute(
        select(Project)
        .join(ProjectTeam, Project.id == ProjectTeam.project_id)
        .where(ProjectTeam.team_id == team_id)
    )
    return result.scalars().all()


def get_project_by_id(db: Session, user_id: UUID, project_id: UUID) -> Project:
    project = _get_project_or_raise(db, project_id)
    _assert_user_in_project(db, user_id, project_id)
    return project


def create_project(db: Session, user_id: UUID, data: ProjectCreate) -> Project:
    _assert_user_in_team(db, user_id, data.team_id)

    new_project = Project(
        name=data.name,
        due_date=data.due_date,
        owner_id=user_id,
    )
    try:
        db.add(new_project)
        db.flush()

        link = ProjectTeam(project_id=new_project.id, team_id=data.team_id)
        db.add(link)

        db.commit()
        db.refresh(new_project)
        return new_project
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Project not created.") from e


def add_team_to_project(
    db: Session, user_id: UUID, project_id: UUID, team_id: UUID
) -> ProjectTeam:
    _get_project_or_raise(db, project_id)
    _assert_user_in_team(db, user_id, team_id)

    existing = db.execute(
        select(ProjectTeam).where(
            ProjectTeam.project_id == project_id,
            ProjectTeam.team_id == team_id,
        )
    ).scalar_one_or_none()

    if existing:
        raise ValueError("Team is already assigned to this project.")

    link = ProjectTeam(project_id=project_id, team_id=team_id)
    try:
        db.add(link)
        db.commit()
        db.refresh(link)
        return link
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Team not added to project.") from e


def edit_project(
    db: Session, user_id: UUID, project_id: UUID, data: ProjectUpdate
) -> Project:
    project = _get_project_or_raise(db, project_id)
    _assert_user_in_project(db, user_id, project_id)

    if project.owner_id != user_id:
        raise ValueError("Only the project owner can edit this project.")

    updates = {"name": data.name, "due_date": data.due_date}
    for field, value in updates.items():
        if value is not None:
            setattr(project, field, value)

    try:
        db.commit()
        db.refresh(project)
        return project
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Project not updated.") from e


def delete_project(db: Session, user_id: UUID, project_id: UUID) -> Project:
    project = _get_project_or_raise(db, project_id)
    _assert_user_in_project(db, user_id, project_id)

    if project.owner_id != user_id:
        raise ValueError("Only the project owner can delete this project.")

    try:
        db.delete(project)
        db.commit()
        return project
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Project not deleted.") from e
