from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    surname: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserLoginRequest(BaseModel):
  email: EmailStr
  password: str = Field(min_length=8, max_length=255)
  
class LoginResponse(BaseModel):
  message: str