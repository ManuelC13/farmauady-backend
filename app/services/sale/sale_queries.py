from sqlalchemy.orm import Session, joinedload
from app.models.sale import Sale
from app.models.detail_sale import DetailSale
from app.models.user import User
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
