from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    __tablename__ = "roles"

    id_role: Mapped[int] = mapped_column(
        "id_role", Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        "name", String(50),
        unique=True, nullable=False
    )

    # Relationship con User
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
