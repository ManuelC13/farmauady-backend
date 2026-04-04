from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, DECIMAL, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.detail_sale import DetailSale


class Sale(Base):
    __tablename__ = "sales"

    id_sale: Mapped[int] = mapped_column(
        "id_sale", Integer,
        primary_key=True,
        autoincrement=True
    )

    id_seller: Mapped[int] = mapped_column(
        "id_seller", ForeignKey("users.id_user"),
        nullable=False
    )

    folio: Mapped[str] = mapped_column(
        "folio", String(50),
        unique=True, nullable=False
    )

    sale_date: Mapped[datetime] = mapped_column(
        "sale_date", DateTime,
        server_default=func.now()
    )

    total: Mapped[float] = mapped_column(
        "total", DECIMAL(10, 2),
        nullable=False
    )

    payment_method: Mapped[Optional[str]] = mapped_column(
        "payment_method", String(50),
        nullable=True
    )

    # Relationships con otras tablas
    seller: Mapped["User"] = relationship("User", back_populates="sales")
    details: Mapped[List["DetailSale"]] = relationship(
        "DetailSale",
        back_populates="sale",
        cascade="all, delete-orphan"
    )