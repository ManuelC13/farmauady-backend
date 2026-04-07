from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.models.password_reset_tokens import PasswordResetToken
from app.utils.security import (
    create_password_reset_token,
    verify_password_reset_token,
    hash_password,
    hash_reset_token,
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES
)
from app.services.auth.email_service import send_reset_password_email


def generate_password_reset_token(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Si el correo existe se te enviara un enlace para restablecer tu contraseña")

    reset_token = create_password_reset_token(email=user.email)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)

    db_token = PasswordResetToken(
        user_id=user.id_user,
        token_hash=hash_reset_token(reset_token),
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()

    send_reset_password_email(user.email, reset_token)

    return reset_token


def reset_password_with_token(db: Session, token: str, new_password: str):
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == hash_reset_token(token),
        PasswordResetToken.user_id == user.id_user
    ).first()

    if not token_record:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    if token_record.used_at is not None:
        raise HTTPException(status_code=400, detail="Este token ya fue utilizado")

    if token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expirado")

    token_record.used_at = datetime.now(timezone.utc)
    user.password_hash = hash_password(new_password)

    db.commit()
    return user
