from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import authenticate, get_db
from app.models.user import User
from app.schemas.team import AddUserToTeamResponse, TeamResponse
from app.services.team_service import create_team, get_teams_for_user_id

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/user-teams", response_model=list[TeamResponse])
def get_user_teams_route(
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> list[TeamResponse]:
    team_list = get_teams_for_user_id(db, current_user.id)
    return team_list


@router.post("/create", response_model=TeamResponse, status_code=status.HTTP_201_CREATED,)
def create_team_route(
    team_name: str,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> TeamResponse:
    new_team = create_team(db, current_user.id, team_name)
    return new_team

@router.post("/add-user", response_model=AddUserToTeamResponse, status_code=status.HTTP_201_CREATED,)
def add_user_to_team_route(
  team_id: str,
  user_id: str,
  current_user: User = Depends(authenticate),
  db: Session = Depends(get_db)
) -> AddUserToTeamResponse:
  new_member = add_user_to_team(db, current_user.id, user_id, team_id)