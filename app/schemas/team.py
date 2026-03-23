from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class TeamMemberResponse(BaseModel):
    user_id: UUID
    team_id: UUID
