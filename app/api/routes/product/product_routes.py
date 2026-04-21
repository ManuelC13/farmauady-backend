from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.product import product_service
from app.schemas.product import ProductSaleListResponse
from typing import Optional

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/sale", response_model=ProductSaleListResponse)
def get_sale_products(
    search: Optional[str] = Query(None, description="Buscar por nombre o categoría"),
    db: Session = Depends(get_db)
):
    return product_service.get_products_for_sale(db, search)