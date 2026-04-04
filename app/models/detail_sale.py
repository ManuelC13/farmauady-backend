from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class DetailSale(Base):
    __tablename__ = 'detail_sale'

    detail_sale_id = Column(Integer, primary_key=True, autoincrement=True)

    sale_id = Column(
        Integer,
        ForeignKey('sale.sale_id', ondelete='CASCADE'),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey('product.product_id'),
        nullable=False
    )

    amount = Column(Integer, nullable=False)

    unit_price = Column(DECIMAL(10, 2), nullable=False)

    subtotal = Column(DECIMAL(10, 2), nullable=False)

    # Relaciones con Sale y Product
    sale = relationship("Sale", back_populates="details")
    product = relationship("Product", back_populates="detail_sales")