from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.category import CategoryResponse
from app.services.product import category_service
from app.services.auth.auth_service import RoleChecker

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse], dependencies=[Depends(RoleChecker(["Administrador", "Vendedor"]))])
def list_categories(db: Session = Depends(get_db)):
    return category_service.get_categories(db)