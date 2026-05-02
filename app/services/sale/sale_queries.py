from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import date
from typing import Optional
from app.models.sale import Sale
from app.models.detail_sale import DetailSale
from app.models.user import User
from app.models.product import Product
from app.schemas.sale import SaleResponse, SaleDetailResponse

def get_recent_sales(db: Session, limit: int = 5, current_user: User = None) -> list[SaleResponse]:
    query = (
        db.query(Sale)
        .options(
            joinedload(Sale.seller),
            joinedload(Sale.details).joinedload(DetailSale.product)
        )
    )

    if current_user and current_user.role.name == "Vendedor":
        query = query.filter(Sale.id_seller == current_user.id_user)

    today = date.today()
    query = query.filter(func.date(Sale.sale_date) == today)

    sales = (
        query.order_by(Sale.sale_date.desc())
        .limit(limit)
        .all()
    )

    responses = []
    for sale in sales:
        detail_responses = []
        for detail in sale.details:
            detail_responses.append(SaleDetailResponse(
                id_product=detail.id_product,
                product_name=detail.product.name,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal=detail.subtotal
            ))
            
        responses.append(SaleResponse(
            id_sale=sale.id_sale,
            folio=sale.folio,
            sale_date=sale.sale_date,
            total=sale.total,
            payment_method=sale.payment_method,
            seller_name=f"{sale.seller.first_name} {sale.seller.last_name}",
            details=detail_responses
        ))
        
        
    return responses

def get_all_sales(db: Session) -> list[SaleResponse]:
    sales = (
        db.query(Sale)
        .options(
            joinedload(Sale.seller),
            joinedload(Sale.details).joinedload(DetailSale.product)
        )
        .order_by(Sale.sale_date.desc())
        .all()
    )

    responses = []
    for sale in sales:
        detail_responses = []
        for detail in sale.details:
            detail_responses.append(SaleDetailResponse(
                id_product=detail.id_product,
                product_name=detail.product.name,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal=detail.subtotal
            ))
            
        responses.append(SaleResponse(
            id_sale=sale.id_sale,
            folio=sale.folio,
            sale_date=sale.sale_date,
            total=sale.total,
            payment_method=sale.payment_method,
            seller_name=f"{sale.seller.first_name} {sale.seller.last_name}",
            details=detail_responses
        ))
        
    return responses

def get_sales_by_seller(db: Session, seller_id: int) -> list[SaleResponse]:
    sales = (
        db.query(Sale)
        .options(
            joinedload(Sale.seller),
            joinedload(Sale.details).joinedload(DetailSale.product)
        )
        .filter(Sale.id_seller == seller_id)
        .order_by(Sale.sale_date.desc())
        .all()
    )

    responses = []
    for sale in sales:
        detail_responses = []
        for detail in sale.details:
            detail_responses.append(SaleDetailResponse(
                id_product=detail.id_product,
                product_name=detail.product.name,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal=detail.subtotal
            ))

        responses.append(SaleResponse(
            id_sale=sale.id_sale,
            folio=sale.folio,
            sale_date=sale.sale_date,
            total=sale.total,
            payment_method=sale.payment_method,
            seller_name=f"{sale.seller.first_name} {sale.seller.last_name}",
            details=detail_responses
        ))

    return responses


    # Obtención de las ventas filtradas. Primero se arma la base de las ventas en el rango 
# de fechas y posteriormente se aplican los demás filtros opcionales
def get_filtered_sales(
    db: Session,
    start_date: date,
    end_date: date,
    seller_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> list[SaleResponse]:
    query = (
        db.query(Sale)
        .options(
            joinedload(Sale.seller),
            joinedload(Sale.details).joinedload(DetailSale.product)
        )
        .filter(
            func.date(Sale.sale_date) >= start_date,
            func.date(Sale.sale_date) <= end_date,
        )
    )

    if seller_id:
        query = query.filter(Sale.id_seller == seller_id)

    if category_id:
        query = query.join(Sale.details).join(DetailSale.product).filter(
            Product.id_category == category_id
        ).distinct()

    sales = query.order_by(Sale.sale_date.desc()).all()

    responses = []
    for sale in sales:
        detail_responses = []
        for detail in sale.details:
            detail_responses.append(SaleDetailResponse(
                id_product=detail.id_product,
                product_name=detail.product.name,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal=detail.subtotal
            ))

        responses.append(SaleResponse(
            id_sale=sale.id_sale,
            folio=sale.folio,
            sale_date=sale.sale_date,
            total=sale.total,
            payment_method=sale.payment_method,
            seller_name=f"{sale.seller.first_name} {sale.seller.last_name}",
            details=detail_responses
        ))

    return responses
