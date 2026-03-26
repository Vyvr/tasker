from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import authenticate, get_db, validate_csrf
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectTeamAdd,
    ProjectUpdate,
)
from app.services.project_service import (
    add_team_to_project,
    create_project,
    delete_project,
    edit_project,
    get_project_by_id,
    get_projects_for_team,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/team/{team_id}", response_model=list[ProjectResponse])
def get_team_projects_route(
    team_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> list[ProjectResponse]:
    try:
        projects = get_projects_for_team(db, current_user.id, team_id)
        return projects
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_route(
    project_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    try:
        project = get_project_by_id(db, current_user.id, project_id)
        return project
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/create",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_route(
    data: ProjectCreate,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> ProjectResponse:
    try:
        new_project = create_project(db, current_user.id, data)
        return new_project
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.post(
    "/add-team",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_team_to_project_route(
    data: ProjectTeamAdd,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> ProjectResponse:
    try:
        add_team_to_project(db, current_user.id, data.project_id, data.team_id)
        return get_project_by_id(db, current_user.id, data.project_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.put("/{project_id}", response_model=ProjectResponse)
def edit_project_route(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> ProjectResponse:
    try:
        updated_project = edit_project(db, current_user.id, project_id, data)
        return updated_project
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.delete("/{project_id}", response_model=ProjectResponse)
def delete_project_route(
    project_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> ProjectResponse:
    try:
        deleted_project = delete_project(db, current_user.id, project_id)
        return deleted_project
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
