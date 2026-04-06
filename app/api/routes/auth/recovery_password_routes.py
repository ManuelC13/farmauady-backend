from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth_schema import forgotPasswordRequest, ResetPasswordRequest, MessageResponse
from app.services.auth.recovery_password_service import generate_password_reset_token, reset_password_with_token
from app.utils.validate_password import validate_password


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: forgotPasswordRequest, db: Session = Depends(get_db)):
    generate_password_reset_token(db, data.email)
    return {"message": "Si la cuenta existe, se enviará un correo con el token de recuperación"}


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    validate_password(data.new_password)
    reset_password_with_token(db, data.token, data.new_password)
    return {"message": "Contraseña actualizada exitosamente"}
