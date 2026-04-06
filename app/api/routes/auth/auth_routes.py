from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.schemas.auth_schema import loginRequest
from app.services.auth.auth_service import login_user, get_new_access_token
from app.db.database import get_db

router = APIRouter()

@router.post("/login")
def login(data: loginRequest, response: Response, db: Session = Depends(get_db)):
    result = login_user(db, data.email, data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    
    token, fresh_token, user = result

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False, #cuando se despliegue se cambia a true porque depende de HTTPS
        samesite="lax",
        max_age=3600
    )

    response.set_cookie(
        key="fresh_token",
        value=fresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800
    )

    return {
        "message": "Login exitoso",
        "user": {
            "id": user.id_user,
            "name": f"{user.first_name} {user.last_name}",
            "role": user.role.name
        }
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("fresh_token")
    return {
        "message": "logout exitoso"
    }

@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    fresh_token = request.cookies.get("fresh_token")
    if not fresh_token:
        raise HTTPException(status_code=401, detail="No existe un token de refresco")

    new_access_token = get_new_access_token(db, fresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )

    return {
        "message": "Token actualizado exitosamente"
    }