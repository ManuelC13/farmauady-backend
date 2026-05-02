from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.database import get_db
from app.schemas.sale import (
    SaleResponse,
    CreateReservationRequest, ReservationResponse, ConfirmSaleRequest,
    SaleStatsResponse
)
from app.services.sale import sale_service
from app.services.auth.auth_service import get_current_user, RoleChecker
from app.models.user import User

router = APIRouter(prefix="/sales", tags=["sales"])



@router.get("/stats/daily", response_model=SaleStatsResponse)
def get_daily_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_daily_stats(db, current_user)


@router.get("/recent", response_model=List[SaleResponse])
def get_recent_sales(
    limit: int = Query(5, description="Número de ventas recientes a obtener"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_recent_sales(db, limit, current_user)


# El vendedor ve solo sus propias ventas
@router.get("/my-sales", response_model=List[SaleResponse], dependencies=[Depends(RoleChecker(["Vendedor"]))])
def get_my_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_sales_by_seller(db, current_user.id_user)


# El admin ve todas las ventas
@router.get("/all", dependencies=[Depends(RoleChecker(["Administrador"]))])
def get_all_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_all_sales(db, page, limit)


# Devuelve el historial de ventas aplicando los filtros que se seleccionen
@router.get("/filtered", response_model=List[SaleResponse], dependencies=[Depends(RoleChecker(["Administrador"]))])
def get_filtered_sales(
    start_date: date = Query(...),
    end_date: date = Query(...),
    seller_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return sale_service.get_filtered_sales(db, start_date, end_date, seller_id, category_id)


#Endpoints para reservas temporales de productos
@router.post("/reserve", response_model=ReservationResponse, status_code=201)
#Se reserva por 15 minutos
def reserve_inventory(
    payload: CreateReservationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.reserve_inventory(db, current_user, payload)


@router.post("/confirm", response_model=SaleResponse, status_code=201)
def confirm_sale(
    payload: ConfirmSaleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.confirm_sale_from_reservation(db, current_user, payload)


@router.delete("/reserve/{cart_session_id}", status_code=200)
def release_reservation(
    cart_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.release_reservation(db, cart_session_id, current_user)