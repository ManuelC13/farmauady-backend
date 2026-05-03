from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.user import admin_dashboard_service
from app.services.auth.auth_service import RoleChecker

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", dependencies=[Depends(RoleChecker(["Administrador"]))])
def get_summary(db: Session = Depends(get_db)):
    return admin_dashboard_service.get_dashboard_summary(db)


@router.get("/chart", dependencies=[Depends(RoleChecker(["Administrador"]))])
def get_chart(
    period: str = Query("week", pattern="^(week|month|year)$"),
    db: Session = Depends(get_db)
):
    return admin_dashboard_service.get_sales_chart(db, period)