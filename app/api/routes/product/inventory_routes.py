from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.inventory import ManualExitCreate, InventoryMovementResponse, InventoryManualExitReportResponse
from app.services.product import inventory_service
from app.services.auth.auth_service import get_current_user, RoleChecker

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/manual-exit", response_model=InventoryMovementResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def manual_exit(
    data: ManualExitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return inventory_service.create_manual_exit(db, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/movements-report", dependencies=[Depends(RoleChecker(["Administrador"]))])
def get_movements_report(db: Session = Depends(get_db)):
    return inventory_service.get_manual_exits_report(db)