from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=3000)
    project_id: UUID
    team_id: UUID
    assignee_id: UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=3000)
    assignee_id: UUID | None = None
    status_id: UUID | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    creator_id: UUID | None
    assignee_id: UUID | None
    project_id: UUID
    team_id: UUID
    status_id: UUID
    created_at: datetime
    updated_at: datetime
