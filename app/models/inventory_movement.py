import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MovementType(enum.Enum):
    ENTRY = "ENTRADA"
    EXIT = "SALIDA"
    SALE = "VENTA"
    ADJUSTMENT = "AJUSTE"
    EXPIRATION = "CADUCIDAD"
    RETURN = "DEVOLUCION"


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id_movement: Mapped[int] = mapped_column(
        "id_movement", Integer,
        primary_key=True,
        autoincrement=True
    )

    id_product: Mapped[int] = mapped_column(
        "id_product", ForeignKey("products.id_product"),
        nullable=False
    )

    id_user: Mapped[int] = mapped_column(
        "id_user", ForeignKey("users.id_user"),
        nullable=False
    )

    movement_type: Mapped[MovementType] = mapped_column(
        "movement_type", Enum(MovementType),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        "quantity", Integer,
        nullable=False
    )

    reason: Mapped[Optional[str]] = mapped_column(
        "reason", String(255),
        nullable=True
    )

    reference: Mapped[Optional[str]] = mapped_column(
        "reference", String(100),
        nullable=True
    )

    movement_date: Mapped[datetime] = mapped_column(
        "movement_date", DateTime,
        server_default=func.now()
    )

    # Relationships con otras tablas
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_movements")
    user: Mapped["User"] = relationship("User", back_populates="inventory_movements")
