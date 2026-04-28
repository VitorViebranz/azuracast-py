import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class RoleSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr
    username: str
    display_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    display_name: str | None = None
    is_active: bool | None = None
    is_super_admin: bool | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_super_admin: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleSchema] = []

    model_config = {"from_attributes": True}
