import re
from fastapi import HTTPException

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
    reglas = [
        (r"[A-Z]", "una mayúscula"),
        (r"[a-z]", "una minúscula"),
        (r"[0-9]", "un número"),
        (r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", "un carácter especial")
    ]

    for patron, mensaje in reglas:
        if not re.search(patron, password):
            raise HTTPException(
                status_code=400, 
                detail=f"La contraseña debe tener al menos {mensaje}"
            )
    
    return True