import enum
from typing import List
from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SqlEnum

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product


class CategoryStatus(enum.Enum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"


class Category(Base):
    __tablename__ = "categories"

    id_category: Mapped[int] = mapped_column(
        "id_category", Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        "name", String(100),
        nullable=False
    )

    #status: Mapped[CategoryStatus] = mapped_column(
    #    "status", Enum(CategoryStatus),
    #    default=CategoryStatus.ACTIVE
    #)

    status: Mapped[CategoryStatus] = mapped_column(
        "status",
        SqlEnum(CategoryStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=CategoryStatus.ACTIVE
    )

    # Relationship con producto
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")