from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.team_members import TeamMember
from app.models.user import User
from app.schemas.team import AddUserToTeamResponse, TeamResponse


def get_teams_for_user_id(db: Session, user_id: UUID) -> list[TeamResponse]:
    """Find teams where user belongs"""
    query = (
        select(Team)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == user_id)
    )
    result = db.execute(query)
    return result.scalars().all()


def create_team(db: Session, owner_id: UUID, team_name: str) -> Team:
    new_team = Team(name=team_name, owner_id=owner_id)
    try:
        db.add(new_team)
        db.flush()

        new_member = TeamMember(user_id=owner_id, team_id=new_team.id)
        db.add(new_member)

        db.commit()
        db.refresh(new_team)
        return new_team
    except Exception as e:
        db.rollback()
        raise RuntimeError("Database error. Team not created.") from e


def add_user_to_team(
    db: Session,
    owner_id: UUID,
    user_id: UUID,
    team_id: UUID,
) -> AddUserToTeamResponse:
    existing_team = db.execute(
        select(Team).where(Team.id == team_id)
    ).scalar_one_or_none()

    if not existing_team:
        raise ValueError("No team with provided id.")

    if existing_team.owner_id != owner_id:
        raise ValueError("User is not allowed to add new members to the team.")

    existing_user = db.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    if not existing_user:
        raise ValueError("No user with provided id.")

    is_a_member = db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id, TeamMember.team_id == team_id
        )
    ).scalar_one_or_none()

    if is_a_member:
        raise ValueError("User is already member of the team.")

    new_member = TeamMember(user_id=user_id, team_id=team_id)
    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        return AddUserToTeamResponse(user_id=str(user_id), team_id=str(team_id))
    except Exception as e:
        db.rollback()
        raise RuntimeError("Can't add new user. Try again later") from e
