import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.models.detail_sale import DetailSale
from app.models.inventory_movement import InventoryMovement, MovementType
from app.models.user import User
from app.schemas.sale import CreateSaleRequest, SaleResponse, SaleDetailResponse

def _generate_folio() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"VNT-{date_part}-{unique_part}"

def create_sale(db: Session, seller: User, payload: CreateSaleRequest) -> SaleResponse:
    try:
        locked_products = {}
        
        """
        ---Bloqueo pesimista de productos y validación de stock---

        Se bloquean los productos para evitar que otro usuario pueda modificarlos
        mientras se realiza la venta. Solo podrá acceder al recurso hasta que el primer
        usuario termine la transacción.
        """
        for item in payload.items:
            product = (
                db.query(Product)
                .filter(Product.id_product == item.id_product)
                .with_for_update() # -> Bloqueo pesimista
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
                    detail=f"Producto {product.name} no esta activo"
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"No hay stock suficiente para {product.name}. "
                        f"Stock actual: {product.stock}, Solicitado: {item.quantity}"
                    )
                )

            locked_products[item.id_product] = product

        total = sum(
            float(locked_products[item.id_product].sale_price) * item.quantity
            for item in payload.items
        )

        """
        ---Creación de la venta y detalles---

        Se crea la venta y se agregan los detalles de la venta.
        """
        folio = _generate_folio()
        new_sale = Sale(
            id_seller = seller.id_user, 
            folio = folio,
            total = total,
            payment_method = payload.payment_method
        )
        db.add(new_sale)
        db.flush() # -> Obtiene el id_sale generado sin hacer el commit a la base de datos todavía

        #Detalles + stock + movimientos
        detail_responses = []

        for item in payload.items:
            product = locked_products[item.id_product]
            unit_price = float(product.sale_price)
            subtotal = unit_price * item.quantity

            detail = DetailSale(
                id_sale = new_sale.id_sale,
                id_product = product.id_product,
                quantity = item.quantity,
                unit_price = unit_price,
                subtotal = subtotal
            )
            db.add(detail)

            product.stock -= item.quantity # -> descontar del stock

            movement = InventoryMovement(
                id_product = product.id_product,
                id_user = seller.id_user,
                movement_type = MovementType.SALE,
                quantity = item.quantity,
                reason = "Venta registrada en el sistema",
                reference = folio
            )
            db.add(movement)

            detail_responses.append(SaleDetailResponse(
                id_product = product.id_product,
                product_name = product.name,
                quantity = item.quantity,
                unit_price = unit_price,
                subtotal = subtotal
            ))

        #Commit TODO O NADA, si falla manda rollback
        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = 500,
            detail = f"Error interno: {str(e)}"
        )
    
    return SaleResponse(
        id_sale = new_sale.id_sale,
        folio = folio,
        sale_date = new_sale.sale_date,
        total = total,
        payment_method = new_sale.payment_method,
        seller_name = f"{seller.first_name} {seller.last_name}",
        details = detail_responses
    )