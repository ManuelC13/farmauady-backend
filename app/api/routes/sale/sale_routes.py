from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.sale import CreateSaleRequest, SaleResponse
from app.services.sale import sale_service
from app.services.auth.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/create", response_model=SaleResponse, status_code=201)
def create_sale(
    payload: CreateSaleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.create_sale(db, current_user, payload)