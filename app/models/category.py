from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

from database import Base

class EnumState(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Category(Base):
    __tablename__ = 'category'

    category_id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(100), nullable=False)

    estate = Column(Enum(EnumState, name="category_state"), nullable=False)

    # Relación con Product
    products = relationship("Product", back_populates="category")