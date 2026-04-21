from sqlalchemy.orm import Session
from app.models.inventory_movement import InventoryMovement, MovementType
from app.models.product import Product
from app.schemas.inventory import ManualExitCreate


def create_manual_exit(db: Session, data: ManualExitCreate, current_user):
    print("movement_type recibido:", data.movement_type)  
    print("allowed_types:", {MovementType.EXIT, MovementType.EXPIRATION, MovementType.RETURN})
    # Verificar que el producto existe y no está eliminado
    product = db.query(Product).filter(
        Product.id_product == data.id_product,
        Product.deleted_at == None
    ).first()

    if not product:
        raise ValueError("Producto no encontrado")

    # Verificar que el tipo de movimiento sea válido para salida manual
    allowed_types = {MovementType.EXIT.value, MovementType.EXPIRATION.value, MovementType.RETURN.value}
    if data.movement_type not in allowed_types:
        raise ValueError("Tipo de movimiento no permitido para salida manual")

    # Verificar stock suficiente
    if data.quantity <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")
    if data.quantity > product.stock:
        raise ValueError(f"Stock insuficiente. Disponible: {product.stock} u.")

    # Registrar movimiento
    movement = InventoryMovement(
        id_product=data.id_product,
        id_user=current_user.id_user,
        movement_type=data.movement_type,
        quantity=data.quantity,
        reason=data.reason,
        reference=data.reference,
    )
    db.add(movement)

    # Descontar stock del producto
    product.stock -= data.quantity

    db.commit()
    db.refresh(movement)

    return movement