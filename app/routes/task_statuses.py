from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import authenticate, get_db
from app.models.user import User
from app.schemas.task_status import TaskStatusResponse
from app.services.task_status_service import get_all_statuses, get_status_by_id

router = APIRouter(prefix="/task-statuses", tags=["Task Statuses"])


@router.get("", response_model=list[TaskStatusResponse])
def get_all_statuses_route(
    _: None = Depends(authenticate),
    db: Session = Depends(get_db),
) -> list[TaskStatusResponse]:
    return get_all_statuses(db)


@router.get("/{status_id}", response_model=TaskStatusResponse)
def get_status_route(
    status_id: UUID,
    _: None = Depends(authenticate),
    db: Session = Depends(get_db),
) -> TaskStatusResponse:
    try:
        return get_status_by_id(db, status_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
