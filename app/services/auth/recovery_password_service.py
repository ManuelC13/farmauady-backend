from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import create_password_reset_token, verify_password_reset_token, hash_password
from app.services.auth.email_service import send_reset_password_email

def generate_password_reset_token(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    reset_token = create_password_reset_token(email=user.email)
    
    send_reset_password_email(user.email, reset_token)
    
    return reset_token

def reset_password_with_token(db: Session, token: str, new_password: str):
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.password_hash = hash_password(new_password)
    
    db.commit()
    return user
