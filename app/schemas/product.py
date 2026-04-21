from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

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

    class Config:
        from_attributes = True

class ProductSaleListResponse(BaseModel):
    total: int
    products: List[ProductForSale]