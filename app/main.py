import os
from dotenv import load_dotenv
load_dotenv()
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
from app.models.inventory_reservation import InventoryReservation  #Reserva de productos
from app.models.product import Product
from app.models.role import Role
from app.models.sale import Sale
from app.models.user import User
from app.models.password_reset_tokens import PasswordResetToken
from app.api.routes.product import product_routes
from app.api.routes.sale import sale_routes

from app.api.routes.user import user_routes
from app.api.routes.user import admin_dashboard_routes
from app.api.routes.product import product_routes
from app.api.routes.product import inventory_routes
from app.api.routes.product import category_routes
from app.api.routes.websockets import inventory_ws
from app.api.routes.websockets import presence_ws

app = FastAPI()

#Limpieza periódica de reservas expiradas (Cada 5 minutos)
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.database import SessionLocal
from app.services.sale.sale_service import cleanup_expired_reservations

scheduler = BackgroundScheduler()

def _run_reservation_cleanup():
    db = SessionLocal()
    try:
        deleted = cleanup_expired_reservations(db)
        if deleted:
            print(f"Reservas expiradas eliminadas {deleted}")
    finally:
        db.close()

scheduler.add_job(_run_reservation_cleanup, 'interval', minutes=5)
scheduler.start()

produccion_url = os.getenv("FRONTEND_URL")

if not produccion_url:
    raise ValueError("¡ERROR CRÍTICO! La variable FRONTEND_URL no está definida en las variables de entorno.")

origenes_permitidos = [
    produccion_url,              
    "http://localhost:5173",     
    "http://localhost:8000",     
    "http://127.0.0.1:8000",
    "https://farmauady.vercel.app",     
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Backend funcionando..."}

app.include_router(auth_routes.router)
app.include_router(recovery_password_routes.router)
app.include_router(user_routes.router)
app.include_router(admin_dashboard_routes.router)
app.include_router(product_routes.router)
app.include_router(inventory_routes.router)
app.include_router(category_routes.router)
app.include_router(sale_routes.router)
app.include_router(inventory_ws.router)
app.include_router(presence_ws.router)