import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.sale import Sale
    from app.models.inventory_movement import InventoryMovement
    from app.models.generated_report import GeneratedReport

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"


class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(
        "id_user", Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    id_role: Mapped[int] = mapped_column(
        "id_role", ForeignKey("roles.id_role"),
        nullable=False
    )

    first_name: Mapped[str] = mapped_column(
        "first_name", String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        "last_name", String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        "email", String(150),
        unique=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        "password_hash", String(255),
        nullable=False
    )

    status: Mapped[UserStatus] = mapped_column(
        "status", Enum(UserStatus),
        default=UserStatus.ACTIVE
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

    # Relationships - relaciones con otras tablas
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="seller")
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship("InventoryMovement", back_populates="user")
    generated_reports: Mapped[List["GeneratedReport"]] = relationship("GeneratedReport", back_populates="user")