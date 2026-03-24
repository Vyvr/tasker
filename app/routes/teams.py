from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import authenticate, get_db, validate_csrf
from app.models.user import User
from app.schemas.team import TeamMemberResponse, TeamResponse
from app.services.team_service import (
    add_user_to_team,
    create_team,
    delete_user_from_team,
    get_teams_for_user_id,
)

#
# @TODO: add PUT and DELETE methods
#

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/user-teams", response_model=list[TeamResponse])
def get_user_teams_route(
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> list[TeamResponse]:
    team_list = get_teams_for_user_id(db, current_user.id)
    return team_list


@router.post(
    "/create",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team_route(
    team_name: str,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> TeamResponse:
    new_team = create_team(db, current_user.id, team_name)
    return new_team


@router.post(
    "/add-user",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_user_to_team_route(
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> TeamMemberResponse:
    try:
        new_member = add_user_to_team(db, current_user.id, user_id, team_id)
        return new_member
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.delete(
    "/delete-user/{user_id}",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_200_OK,
)
def delete_user_from_team_route(
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> TeamMemberResponse:

    try:
        deleted_member = delete_user_from_team(db, current_user.id, user_id, team_id)
        return deleted_member
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
