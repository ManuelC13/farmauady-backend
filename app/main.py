from fastapi import FastAPI
from app.db.database import engine
from app.db.base_class import Base

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

from app.api.routes import user_routes

app = FastAPI()

#Base.metadata.create_all(bind=engine)

app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Backend funcionando..."}