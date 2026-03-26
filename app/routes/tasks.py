from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import authenticate, get_db, validate_csrf
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import (
    create_task,
    delete_task,
    edit_task,
    get_task_by_id,
    get_tasks_for_project,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/project/{project_id}", response_model=list[TaskResponse])
def get_project_tasks_route(
    project_id: UUID,
    team_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> list[TaskResponse]:
    try:
        tasks = get_tasks_for_project(db, current_user.id, project_id, team_id)
        return tasks
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_route(
    task_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
) -> TaskResponse:
    try:
        task = get_task_by_id(db, current_user.id, task_id)
        return task
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/create",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_route(
    data: TaskCreate,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> TaskResponse:
    try:
        new_task = create_task(db, current_user.id, data)
        return new_task
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.put("/{task_id}", response_model=TaskResponse)
def edit_task_route(
    task_id: UUID,
    data: TaskUpdate,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> TaskResponse:
    try:
        updated_task = edit_task(db, current_user.id, task_id, data)
        return updated_task
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.delete("/{task_id}", response_model=TaskResponse)
def delete_task_route(
    task_id: UUID,
    current_user: User = Depends(authenticate),
    db: Session = Depends(get_db),
    _: None = Depends(validate_csrf),
) -> TaskResponse:
    try:
        deleted_task = delete_task(db, current_user.id, task_id)
        return deleted_task
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
