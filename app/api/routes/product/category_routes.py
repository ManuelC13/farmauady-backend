from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.product import category_service
from app.services.auth.auth_service import RoleChecker

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse], dependencies=[Depends(RoleChecker(["Administrador"]))])
def list_categories(db: Session = Depends(get_db)):
    return category_service.get_categories(db)


@router.post("/", response_model=CategoryResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    try:
        return category_service.create_category(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = category_service.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    try:
        return category_service.update_category(db, category, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", dependencies=[Depends(RoleChecker(["Administrador"]))])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = category_service.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    try:
        category_service.delete_category(db, category)
        return {"message": "Categoría desactivada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))