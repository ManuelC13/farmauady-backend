from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.product import product_service
from app.schemas.product import ProductSaleListResponse, ProductCreate, ProductUpdate, ProductResponse
from typing import Optional, List
from app.services.auth.auth_service import get_current_user, RoleChecker

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/sale", response_model=ProductSaleListResponse)
def get_sale_products(
    search: Optional[str] = Query(None, description="Buscar por nombre o categoría"),
    cart_session_id: Optional[str] = Query(None, description="ID de la sesión del carrito"),
    db: Session = Depends(get_db)
):
    return product_service.get_products_for_sale(db, search, cart_session_id)
    

# Devuelve los productos que se mostrarán en el reporte 
@router.get("/inventory-report", response_model=List[ProductResponse], dependencies=[Depends(RoleChecker(["Administrador"]))])
def get_inventory_report(db: Session = Depends(get_db)):
    return product_service.get_products(db)


@router.get("/", response_model=List[ProductResponse], dependencies=[Depends(RoleChecker(["Administrador", "Vendedor"]))])
def list_products(db: Session = Depends(get_db)):
    return product_service.get_products(db)


@router.get("/{product_id}", response_model=ProductResponse, dependencies=[Depends(RoleChecker(["Administrador", "Vendedor"]))])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return product


@router.post("/", response_model=ProductResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        return product_service.create_product(db, product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}", response_model=ProductResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def update_product(product_id: int, updates: ProductUpdate, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    try:
        return product_service.update_product(db, product, updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", dependencies=[Depends(RoleChecker(["Administrador"]))])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    try:
        product_service.delete_product(db, product)
        return {"message": "Producto eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
