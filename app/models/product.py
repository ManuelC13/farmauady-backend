from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import Boolean, Date, DateTime, DECIMAL, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.detail_sale import DetailSale
    from app.models.inventory_movement import InventoryMovement


class Product(Base):
    __tablename__ = "products"

    id_product: Mapped[int] = mapped_column(
        "id_product", Integer,
        primary_key=True,
        autoincrement=True
    )

    id_category: Mapped[int] = mapped_column(
        "id_category", ForeignKey("categories.id_category"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        "name", String(150),
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(
        "description", Text,
        nullable=True
    )

    sku: Mapped[str] = mapped_column(
        "sku", String(100),
        unique=True, nullable=False
    )

    sale_price: Mapped[float] = mapped_column(
        "sale_price", DECIMAL(10, 2),
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        "stock", Integer,
        nullable=False, default=0
    )

    minimum_stock: Mapped[int] = mapped_column(
        "minimum_stock", Integer,
        nullable=False, default=10
    )

    expiration_date: Mapped[date] = mapped_column(
        "expiration_date", Date,
        nullable=True
    )

    batch: Mapped[Optional[str]] = mapped_column(
        "batch", String(100),
        nullable=True
    )

    active: Mapped[bool] = mapped_column(
        "active", Boolean,
        nullable=False, default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime,
        server_default=func.now(), onupdate=func.now()
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        "deleted_at", DateTime,
        nullable=True
    )

    # Relationships con otras tablas
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    sale_details: Mapped[List["DetailSale"]] = relationship("DetailSale", back_populates="product")
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship("InventoryMovement", back_populates="product")