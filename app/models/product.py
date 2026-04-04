from sqlalchemy import (
    Column, Integer, String, Text, Date, Boolean,
    DECIMAL, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True, autoincrement=True)

    category_id = Column(Integer, ForeignKey('category.category_id'), nullable=False)
    category = relationship("Category", back_populates="products")

    name = Column(String(150), nullable=False)

    description = Column(Text)

    sku = Column(String(100), unique=True, nullable=False)

    price = Column(DECIMAL(10, 2), nullable=False)

    stock = Column(Integer, nullable=False)

    minimum_stock = Column(Integer, nullable=False)

    expiration_date = Column(Date, nullable=True)

    batch = Column(String(100))

    active = Column(Boolean, nullable=False, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    deleted_at = Column(TIMESTAMP, nullable=True)

    detail_sales = relationship("DetailSale", back_populates="product")