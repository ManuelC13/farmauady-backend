from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.sale import Sale
from app.models.detail_sale import DetailSale
from app.models.user import User

def get_daily_stats(db: Session, current_user: User) -> dict:
    today = datetime.now().date()

    total_sales = (
        db.query(func.sum(Sale.total))
        .filter(
            Sale.id_seller == current_user.id_user,
            func.date(Sale.sale_date) == today
        )
        .scalar() or 0
    )

    items_sold = (
        db.query(func.sum(DetailSale.quantity))
        .join(Sale)
        .filter(
            Sale.id_seller == current_user.id_user,
            func.date(Sale.sale_date) == today
        )
        .scalar() or 0
    )

    return {
        "total_sales": total_sales,
        "items_sold": items_sold
    }
