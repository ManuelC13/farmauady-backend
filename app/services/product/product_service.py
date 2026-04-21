from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.models.category import Category

def get_products_for_sale(db: Session, search: str = None):
    query = db.query(
        Product.id_product,
        Product.name,
        Category.name.label("category_name"),
        Product.sale_price,
        Product.stock,
        Product.minimum_stock
    ).join(Category, Product.id_category == Category.id_category)\
    .filter(Product.active == True)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Category.name.ilike(search_filter)
            )
        )
    
    products = query.all()

    return {
        "total": len(products),
        "products": products
    }