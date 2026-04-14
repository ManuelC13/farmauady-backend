from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth_schema import loginRequest, LoginResponse, MessageResponse
from app.services.auth.auth_service import login_user, get_new_access_token, get_current_user
from app.api.dependencies import check_login_rate_limit

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
def login(
    data: loginRequest, 
    response: Response, 
    db: Session = Depends(get_db),
    rate_limit = Depends(check_login_rate_limit)
):
    result = login_user(db, data.email, data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    
    token, fresh_token, user = result

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False, # cuando se despliegue se cambia a true porque depende de HTTPS
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


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("fresh_token")
    return {
        "message": "logout exitoso"
    }


@router.post("/refresh", response_model=MessageResponse)
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


@router.get("/verify")
def verify_session(user: dict = Depends(get_current_user)):
    """Verifica si la cookie HttpOnly sigue activa y retorna los datos del usuario."""
    return {
        "user": {
            "id": user.id_user,
            "name": f"{user.first_name} {user.last_name}",
            "role": user.role.name
        }
    }
