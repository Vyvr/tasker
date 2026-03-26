from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    due_date: datetime | None = None
    team_id: UUID


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    due_date: datetime | None = None


class ProjectTeamAdd(BaseModel):
    project_id: UUID
    team_id: UUID


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    owner_id: UUID
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
