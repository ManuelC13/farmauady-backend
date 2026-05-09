from fastapi import Request, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus
from sqlalchemy.orm import joinedload
from app.utils.security import verify_password, create_access_token, verify_token, create_fresh_token, verify_fresh_token
from app.db.database import get_db

def login_user(db: Session, email: str, password: str):
    user = db.query(User).options(joinedload(User.role)).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Esta cuenta ha sido eliminada")

    if user.status == UserStatus.INACTIVE:
        raise HTTPException(status_code=401, detail="Usuario inactivo. Contacte al administrador.")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({
        "sub": str(user.id_user),
        "email": user.email,
        "role": user.role.name
    })

    fresh_token = create_fresh_token({
        "sub": str(user.id_user)
    })

    return token, fresh_token, user

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = payload.get("sub")
    user = db.query(User).options(joinedload(User.role)).filter(User.id_user == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if user.deleted_at is not None or user.status == UserStatus.INACTIVE:
        raise HTTPException(status_code=401, detail="Sesión inválida: Usuario inactivo o eliminado")

    return user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Acceso denegado. Rol inválido"
            )
        return user

def get_new_access_token(db:Session, token:str):
    payload = verify_fresh_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    user_id = payload.get("sub")

    user = db.query(User).options(joinedload(User.role)).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    if user.deleted_at is not None or user.status == UserStatus.INACTIVE:
        raise HTTPException(status_code=401, detail="No se puede renovar el token para un usuario inactivo o eliminado")

    new_access_token = create_access_token({
        "sub": str(user.id_user),
        "email": user.email,
        "role": user.role.name
    })

    return new_access_token

#Función para obtener al usuario desde un WebSocket usando el token de acceso en las cookies HttpOnly
def get_user_from_websocket(websocket: WebSocket, db: Session):
    """
    Valida la sesión de un usuario desde un WebSocket.
    Lee la cookie HttpOnly de access_token y verifica que es válido.
    Retorna el usuario o None si la sesión es inválida.
    """
    try:
        token = websocket.cookies.get("access_token")
        
        if not token:
            return None
        
        payload = verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        user = db.query(User).options(joinedload(User.role)).filter(User.id_user == user_id).first()
        
        if not user:
            return None
        
        if user.deleted_at is not None or user.status == UserStatus.INACTIVE:
            return None
        
        return user
    except Exception:
        return None