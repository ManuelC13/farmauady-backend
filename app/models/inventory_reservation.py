from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class InventoryReservation(Base):
    
    __tablename__ = "inventory_reservations"

    id_reservation: Mapped[int] = mapped_column(
        "id_reservation", Integer,
        primary_key=True,
        autoincrement=True
    )

    id_product: Mapped[int] = mapped_column(
        # No se puede eliminar un producto con reservas activas.
        # Obliga a cancelar reservas antes de borrar el producto.
        "id_product", ForeignKey("products.id_product", ondelete="RESTRICT"),
        nullable=False
    )

    id_seller: Mapped[int] = mapped_column(
        # Si un vendedor es eliminado, sus reservas se limpian
        # automáticamente para evitar registros huérfanos.
        "id_seller", ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        "quantity", Integer,
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        "expires_at", DateTime,
        nullable=False
    )

    # ID único de la sesión de venta del vendedor.
    cart_session_id: Mapped[str] = mapped_column(
        "cart_session_id", String(100),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime,
        default=datetime.utcnow
    )

    product: Mapped["Product"] = relationship("Product")
    seller: Mapped["User"] = relationship("User")
