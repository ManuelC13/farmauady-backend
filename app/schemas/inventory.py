from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class MovementType(str, Enum):
    ENTRY = "ENTRADA"
    EXIT = "SALIDA"
    SALE = "VENTA"
    ADJUSTMENT = "AJUSTE"
    EXPIRATION = "CADUCIDAD"
    RETURN = "DEVOLUCION"


class ManualExitCreate(BaseModel):
    id_product: int
    quantity: int
    movement_type: MovementType
    reason: Optional[str] = None
    reference: Optional[str] = None


class InventoryMovementResponse(BaseModel):
    id_movement: int
    id_product: int
    id_user: int
    movement_type: MovementType
    quantity: int
    reason: Optional[str]
    reference: Optional[str]
    movement_date: datetime

    class Config:
        from_attributes = True


class InventoryManualExitReportResponse(BaseModel):
    id_movement: int
    product_name: str
    quantity: int
    movement_type: str
    reason: Optional[str]
    user_name: str
    movement_date: datetime

    class Config:
        from_attributes = True