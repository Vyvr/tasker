from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    color_hash: str
    created_at: datetime
    updated_at: datetime
