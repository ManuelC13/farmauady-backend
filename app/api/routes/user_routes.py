from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service

from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user_service.update_user(db, user, updates)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_service.delete_user(db, user)
    return {"message": "Usuario eliminado exitosamente"}