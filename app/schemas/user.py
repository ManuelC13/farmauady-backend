from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"

class RoleResponse(BaseModel):
    id_role: int
    name: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    id_role: int
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id_user: int
    id_role: int
    first_name: str
    last_name: str
    email: EmailStr
    status: UserStatus

    role: RoleResponse

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None