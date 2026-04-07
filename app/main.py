from fastapi import FastAPI
from app.db.database import engine
from app.db.base_class import Base

from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import auth_routes, recovery_password_routes

from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

# importar modelos
from app.models.category import Category
from app.models.detail_sale import DetailSale
from app.models.generated_report import GeneratedReport
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.models.role import Role
from app.models.sale import Sale
from app.models.user import User
from app.models.password_reset_tokens import PasswordResetToken

from app.api.routes import user_routes

app = FastAPI()

#Esto debe cambiar cuando se haga el fronten y cuando se vaya a subir a producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #Aqui se puede agregar la URL del frontend y el localhost:8000 para probar con el dccs de fastapi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Backend funcionando..."}

app.include_router(auth_routes.router)
app.include_router(recovery_password_routes.router)