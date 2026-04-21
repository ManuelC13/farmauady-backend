from pydantic import BaseModel, condecimal
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime


class ProductForSale(BaseModel):
    id_product: int
    name: str
    category_name: str
    sale_price: Decimal
    stock: int
    minimum_stock: int

    @property
    def is_critical(self) -> bool:
        return self.stock <= self.minimum_stock


class CategoryResponse(BaseModel):
    id_category: int
    name: str

    class Config:
        from_attributes = True

class ProductSaleListResponse(BaseModel):
    total: int
    products: List[ProductForSale]

class ProductCreate(BaseModel):
    id_category: int
    name: str
    description: Optional[str] = None
    #sku: Optional[str] = None
    sale_price: Decimal
    stock: int = 0
    minimum_stock: int = 10
    expiration_date: date
    batch: Optional[str] = None
    active: bool = True


class ProductUpdate(BaseModel):
    id_category: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    sale_price: Optional[Decimal] = None
    stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    expiration_date: Optional[date] = None
    batch: Optional[str] = None
    active: Optional[bool] = None


class ProductResponse(BaseModel):
    id_product: int
    id_category: int
    name: str
    description: Optional[str]
    sku: str
    sale_price: Decimal
    stock: int
    minimum_stock: int
    expiration_date: date
    batch: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    category: CategoryResponse

    class Config:
        from_attributes = True
