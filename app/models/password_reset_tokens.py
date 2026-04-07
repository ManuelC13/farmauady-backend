from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(
        "id", Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey("users.id_user"),
        nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        "token_hash", String(64),
        nullable=False,
        unique=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        "expires_at", DateTime,
        nullable=False
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        "used_at", DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime,
        server_default=func.now()
    )

    # Relación con user
    user: Mapped["User"] = relationship("User")