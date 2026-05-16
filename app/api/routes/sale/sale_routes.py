from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.database import get_db
from app.schemas.sale import (
    SaleResponse, SaleListResponse,
    CreateReservationRequest, ReservationResponse, ConfirmSaleRequest,
    SaleStatsResponse
)
from app.services.sale import sale_service
from app.services.auth.auth_service import get_current_user, RoleChecker
from app.models.user import User
from app.services.websockets.manager import manager

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/stats/daily", response_model=SaleStatsResponse)
def get_daily_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_daily_stats(db, current_user)


@router.get("/recent", response_model=SaleListResponse)
def get_recent_sales(
    limit: int = Query(5, description="Número de ventas recientes a obtener"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_recent_sales(db, limit, current_user)


# El vendedor ve solo sus propias ventas
@router.get("/my-sales", response_model=SaleListResponse, dependencies=[Depends(RoleChecker(["Vendedor"]))])
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
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    seller_id: int | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_all_sales(db, page, limit, start_date, end_date, seller_id, search)


# Devuelve el historial de ventas aplicando los filtros que se seleccionen
@router.get("/filtered", response_model=SaleListResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
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
async def reserve_inventory(
    payload: CreateReservationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = sale_service.reserve_inventory(db, current_user, payload)
    # Usamos un broadcast para notificar a todos los vendedores conectados que el inventario cambió
    background_tasks.add_task(manager.broadcast, "INVENTORY_UPDATE")
    return result


@router.post("/confirm", response_model=SaleResponse, status_code=201)
async def confirm_sale(
    payload: ConfirmSaleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = sale_service.confirm_sale_from_reservation(db, current_user, payload)
    background_tasks.add_task(manager.broadcast, "INVENTORY_UPDATE")
    return result


@router.delete("/reserve/{cart_session_id}", status_code=200)
async def release_reservation(
    cart_session_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = sale_service.release_reservation(db, cart_session_id, current_user)
    background_tasks.add_task(manager.broadcast, "INVENTORY_UPDATE")
    return result