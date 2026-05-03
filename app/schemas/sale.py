from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class SaleItemRequest(BaseModel):
    id_product: int
    quantity: int = Field(..., gt=0)

class CreateSaleRequest(BaseModel):
    items: List[SaleItemRequest] = Field(..., min_length=1)
    payment_method: Optional[str] = Field(None, max_length=50)

class SaleDetailResponse(BaseModel):
    id_product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id_sale: int
    folio: str
    sale_date: datetime
    total: Decimal
    payment_method: Optional[str]
    seller_name: str
    details: List[SaleDetailResponse]

    class Config:
        from_attributes = True

class SaleListResponse(BaseModel):
    total: Optional[int] = None
    data: List[SaleResponse]

#Eschemas para la reserva de inventario
class ReserveItemRequest(BaseModel):
    id_product: int
    quantity: int = Field(..., gt=0)


class CreateReservationRequest(BaseModel):
    cart_session_id: str = Field(..., description="UUID único del carrito del vendedor")
    items: List[ReserveItemRequest] = Field(..., min_length=1)
    ttl_minutes: int = Field(15, ge=1, le=60, description="Minutos que dura la reserva")


class ReservationItemResponse(BaseModel):
    id_reservation: int
    id_product: int
    product_name: str
    quantity: int
    expires_at: datetime

    class Config:
        from_attributes = True


class ReservationResponse(BaseModel):
    cart_session_id: str
    items: List[ReservationItemResponse]
    expires_at: datetime

    class Config:
        from_attributes = True


class ConfirmSaleRequest(BaseModel):
    cart_session_id: str
    payment_method: Optional[str] = Field(None, max_length=50)


class SaleStatsResponse(BaseModel):
    total_sales: Decimal
    items_sold: int
