from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class Sale(Base):
    __tablename__ = 'sale'

    sale_id = Column(Integer, primary_key=True, autoincrement=True)

    seller_id = Column(Integer, ForeignKey('seller.seller_id'), nullable=False)

    folio = Column(String(50), unique=True, nullable=False)

    sale_date = Column(TIMESTAMP, server_default=func.now())

    total = Column(DECIMAL(10, 2), nullable=False)

    payment_method = Column(String(50), nullable=True)

    # Relación con User
    seller = relationship("Seller", back_populates="sale")

    details = relationship(
    "DetailSale",
    back_populates="sale",
    cascade="all, delete-orphan"
    )