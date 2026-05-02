from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.auth_schema import ChangePasswordRequest, MessageResponse
from app.services.user import user_service
from app.services.auth.auth_service import get_current_user, RoleChecker
from app.utils.security import verify_password, hash_password
from app.utils.validate_password import validate_password
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", dependencies=[Depends(RoleChecker(["Administrador"]))])
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return user_service.get_users(db, page, limit)


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


@router.put("/me", response_model=UserResponse)
def update_own_profile(
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return user_service.update_user(db, current_user, updates)


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(RoleChecker(["Administrador"]))])
def update_user(
    user_id: int,
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.id_user == current_user.id_user:
        raise HTTPException(status_code=403, detail="No puedes editarte a ti mismo desde este panel")

    if user.role.name != "Vendedor":
        raise HTTPException(status_code=403, detail="No puedes editar usuarios con rol Administrador")

    return user_service.update_user(db, user, updates)


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


@router.patch("/me/change-password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas nuevas no coinciden")

    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="La contraseña actual es incorrecta")

    validate_password(data.new_password)

    current_user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}