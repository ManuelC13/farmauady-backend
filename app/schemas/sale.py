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

