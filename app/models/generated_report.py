import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class ReportType(enum.Enum):
    SALES = "VENTAS"
    INVENTORY = "INVENTARIO"


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id_report: Mapped[int] = mapped_column(
        "id_report", Integer,
        primary_key=True,
        autoincrement=True
    )

    id_user: Mapped[int] = mapped_column(
        "id_user", ForeignKey("users.id_user"),
        nullable=False
    )

    report_type: Mapped[ReportType] = mapped_column(
        "report_type", Enum(ReportType),
        nullable=False
    )

    start_date: Mapped[Optional[date]] = mapped_column(
        "start_date", Date,
        nullable=True
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        "end_date", Date,
        nullable=True
    )

    generation_date: Mapped[datetime] = mapped_column(
        "generation_date", DateTime,
        server_default=func.now()
    )

    # Relationship con User
    user: Mapped["User"] = relationship("User", back_populates="generated_reports")
