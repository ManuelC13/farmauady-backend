from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product
from app.models.inventory_reservation import InventoryReservation
from app.models.user import User
from app.schemas.sale import (
    CreateReservationRequest, ReservationResponse, ReservationItemResponse
)

#Reservas temporales de productos
def _get_available_stock(db: Session, product_id: int) -> int:
    product = db.query(Product).filter(Product.id_product == product_id).first()
    if not product:
        return 0

    reserved = (
        db.query(func.sum(InventoryReservation.quantity))
        .filter(
            InventoryReservation.id_product == product_id,
            InventoryReservation.expires_at > datetime.utcnow()  # Solo reservas ACTIVAS
        )
        .scalar() or 0
    )

    return product.stock - reserved


def reserve_inventory(
    db: Session,
    seller: User,
    payload: CreateReservationRequest
) -> ReservationResponse:
    """
    Reserva los ítems del carrito del vendedor.

    - Verifica stock disponible (stock real − reservas activas).
    """
    try:
        expires_at = datetime.utcnow() + timedelta(minutes=payload.ttl_minutes)
        #Actualiza o crea las reservas
        db.query(InventoryReservation).filter(
            InventoryReservation.cart_session_id == payload.cart_session_id
        ).delete(synchronize_session=False)

        created_items = []

        for item in payload.items:
            product = (
                db.query(Product)
                .filter(Product.id_product == item.id_product)
                .with_for_update()
                .first()
            )

            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto con ID {item.id_product} no encontrado"
                )

            if not product.active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Producto '{product.name}' no está activo"
                )

            available = _get_available_stock(db, item.id_product)

            if available < item.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Stock insuficiente para '{product.name}'. "
                        f"Disponible: {available}, Solicitado: {item.quantity}"
                    )
                )

            reservation = InventoryReservation(
                id_product=item.id_product,
                id_seller=seller.id_user,
                quantity=item.quantity,
                expires_at=expires_at,
                cart_session_id=payload.cart_session_id
            )
            db.add(reservation)
            db.flush()  # Obtiene el id_reservation sin hacer commit todavía

            created_items.append(ReservationItemResponse(
                id_reservation=reservation.id_reservation,
                id_product=product.id_product,
                product_name=product.name,
                quantity=item.quantity,
                expires_at=expires_at
            ))

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al reservar: {str(e)}")

    return ReservationResponse(
        cart_session_id=payload.cart_session_id,
        items=created_items,
        expires_at=expires_at
    )


def release_reservation(db: Session, cart_session_id: str, seller: User) -> dict:
    deleted = (
        db.query(InventoryReservation)
        .filter(
            InventoryReservation.cart_session_id == cart_session_id,
            InventoryReservation.id_seller == seller.id_user
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"Reservas liberadas": deleted, "ID del carrito": cart_session_id}

def cleanup_expired_reservations(db: Session) -> int:
    deleted = (
        db.query(InventoryReservation)
        .filter(InventoryReservation.expires_at <= datetime.utcnow())
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted
