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
    return {}
