from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.models.sale import Sale
from app.models.product import Product
from app.models.user import User


def get_dashboard_summary(db: Session) -> dict:
    today = date.today()

    # Ventas del día
    daily_total = db.query(func.sum(Sale.total)).filter(
        func.date(Sale.sale_date) == today
    ).scalar() or 0

    # Productos en stock
    total_stock = db.query(Product).filter(
        Product.deleted_at == None,
        Product.active == True
    ).count()

    # Productos con stock bajo o igual al mínimo
    low_stock_count = db.query(Product).filter(
        Product.deleted_at == None,
        Product.active == True,
        Product.stock <= Product.minimum_stock
    ).count()

    # Usuarios activos
    active_users = db.query(User).filter(
        User.deleted_at == None,
        User.status == "ACTIVO"
    ).count()

    return {
        "daily_sales":      float(daily_total),
        "total_stock":      int(total_stock),
        "low_stock_count":  low_stock_count,
        "active_users":     active_users,
    }


def get_sales_chart(db: Session, period: str) -> list:
    today = date.today()

    if period == "week":
        start = today - timedelta(days=6)
    elif period == "month":
        start = today - timedelta(days=29)
    else:  # year
        start = date(today.year, 1, 1)

    if period in ("week", "month"):
        rows = (
            db.query(
                func.date(Sale.sale_date).label("period"),
                func.sum(Sale.total).label("total")
            )
            .filter(func.date(Sale.sale_date) >= start)
            .group_by(func.date(Sale.sale_date))
            .order_by(func.date(Sale.sale_date))
            .all()
        )

        sales_map = {str(row.period): float(row.total) for row in rows}
        result = []
        for i in range((today - start).days + 1):
            day = start + timedelta(days=i)
            result.append({
                "period": day.strftime("%Y-%m-%d"),
                "total":  sales_map.get(str(day), 0.0)
            })
        return result

    else:  # year
        rows = (
            db.query(
                func.date_format(Sale.sale_date, "%Y-%m").label("period"),
                func.sum(Sale.total).label("total")
            )
            .filter(func.date(Sale.sale_date) >= start)
            .group_by(func.date_format(Sale.sale_date, "%Y-%m"))
            .order_by(func.date_format(Sale.sale_date, "%Y-%m"))
            .all()
        )

        # Rellenar meses sin ventas con 0
        sales_map = {row.period: float(row.total) for row in rows}
        result = []
        for month in range(1, today.month + 1):
            key = f"{today.year}-{month:02d}"
            result.append({"period": key, "total": sales_map.get(key, 0.0)})
        return result