from fastapi import Request, HTTPException
from app.utils.rate_limiter import login_limiter

def check_login_rate_limit(request: Request):
    client_ip = request.client.host

    if login_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos de inicio de sesión. Intente de nuevo en un minuto."
        )