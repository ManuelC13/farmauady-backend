from pydantic import BaseModel
from enum import Enum


class CategoryStatus(str, Enum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id_category: int
    name: str
    status: CategoryStatus

    class Config:
        from_attributes = True