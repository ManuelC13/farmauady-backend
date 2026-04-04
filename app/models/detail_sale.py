from sqlalchemy import DECIMAL, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class DetailSale(Base):
    __tablename__ = "sale_details"

    id_detail_sale: Mapped[int] = mapped_column(
        "id_detail_sale", Integer,
        primary_key=True,
        autoincrement=True
    )

    id_sale: Mapped[int] = mapped_column(
        "id_sale", ForeignKey("sales.id_sale", ondelete="CASCADE"),
        nullable=False
    )

    id_product: Mapped[int] = mapped_column(
        "id_product", ForeignKey("products.id_product"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        "quantity", Integer,
        nullable=False
    )

    unit_price: Mapped[float] = mapped_column(
        "unit_price", DECIMAL(10, 2),
        nullable=False
    )

    subtotal: Mapped[float] = mapped_column(
        "subtotal", DECIMAL(10, 2),
        nullable=False
    )

    # Relationships con otras tablas
    sale: Mapped["Sale"] = relationship("Sale", back_populates="details")
    product: Mapped["Product"] = relationship("Product", back_populates="sale_details")