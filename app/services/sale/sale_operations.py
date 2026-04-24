import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.models.detail_sale import DetailSale
from app.models.inventory_movement import InventoryMovement, MovementType
from app.models.inventory_reservation import InventoryReservation
from app.models.user import User
from app.schemas.sale import (
    SaleResponse, SaleDetailResponse, ConfirmSaleRequest
)

def _generate_folio() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"VNT-{date_part}-{unique_part}"

def confirm_sale_from_reservation(
    db: Session,
    seller: User,
    payload: ConfirmSaleRequest
) -> SaleResponse:
    try:
        reservations = (
            db.query(InventoryReservation)
            .filter(
                InventoryReservation.cart_session_id == payload.cart_session_id,
                InventoryReservation.id_seller == seller.id_user,
                InventoryReservation.expires_at > datetime.utcnow()
            )
            .order_by(InventoryReservation.id_product.asc())  # ← Prevención de deadlock (se bloqueen mal)
            .all()
        )

        if not reservations:
            raise HTTPException(
                status_code=409,
                detail=(
                    "El carrito no tiene reservas activas o han expirado. "
                    "Por favor, vuelve a agregar los productos al carrito."
                )
            )

        # Bloqueo pesimista
        locked_products = {}
        for res in reservations:
            product = (
                db.query(Product)
                .filter(Product.id_product == res.id_product)
                .with_for_update()
                .first()
            )

            if product is None or not product.active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Producto con ID {res.id_product} no está disponible"
                )

            # Doble verificación
            if product.stock < res.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Stock insuficiente para '{product.name}' al confirmar. "
                        f"Stock actual: {product.stock}, Reservado: {res.quantity}"
                    )
                )

            locked_products[res.id_product] = (product, res.quantity)

        # Calcular total
        total = sum(
            float(product.sale_price) * qty
            for product, qty in locked_products.values()
        )

        # Crear la venta
        folio = _generate_folio()
        new_sale = Sale(
            id_seller=seller.id_user,
            folio=folio,
            total=total,
            payment_method=payload.payment_method
        )
        db.add(new_sale)
        db.flush()  # Obtiene id_sale sin hacer commit todavía

        detail_responses = []

        for res in reservations:
            product, qty = locked_products[res.id_product]
            unit_price = float(product.sale_price)
            subtotal = unit_price * qty

            # Detalle de venta
            detail = DetailSale(
                id_sale=new_sale.id_sale,
                id_product=product.id_product,
                quantity=qty,
                unit_price=unit_price,
                subtotal=subtotal
            )
            db.add(detail)

            # Descontar stock real
            product.stock -= qty

            # Registrar movimiento de inventario para auditoría
            movement = InventoryMovement(
                id_product=product.id_product,
                id_user=seller.id_user,
                movement_type=MovementType.SALE,
                quantity=qty,
                reason="Venta confirmada desde carrito reservado",
                reference=folio
            )
            db.add(movement)

            detail_responses.append(SaleDetailResponse(
                id_product=product.id_product,
                product_name=product.name,
                quantity=qty,
                unit_price=unit_price,
                subtotal=subtotal
            ))

        # Eliminar reservas
        db.query(InventoryReservation).filter(
            InventoryReservation.cart_session_id == payload.cart_session_id
        ).delete(synchronize_session=False)

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al confirmar venta: {str(e)}")

    return SaleResponse(
        id_sale=new_sale.id_sale,
        folio=folio,
        sale_date=new_sale.sale_date,
        total=total,
        payment_method=new_sale.payment_method,
        seller_name=f"{seller.first_name} {seller.last_name}",
        details=detail_responses
    )
