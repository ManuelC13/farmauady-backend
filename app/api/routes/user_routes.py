from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service
from app.services.auth.auth_service import get_current_user, RoleChecker
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[UserResponse],dependencies=[Depends(RoleChecker(["Administrador"]))])
def list_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if current_user.role.name != "Administrador" and current_user.id_user != user_id:
        raise HTTPException(status_code=403, detail="No autorizado") # Si no es su propio perfil ni es admin, no puede verlo

    return user


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user_service.update_user(db, user, updates)


'''@router.delete("/{user_id}", dependencies=[Depends(RoleChecker(["Administrador"]))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_service.delete_user(db, user)
    return {"message": "Usuario eliminado exitosamente"}'''


@router.delete("/{user_id}", dependencies=[Depends(RoleChecker(["Administrador"]))])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        user_service.delete_user(db, user, current_user)
        return {"message": "Usuario eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))