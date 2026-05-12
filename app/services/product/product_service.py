from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.models.category import Category
import uuid
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.inventory_reservation import InventoryReservation
from sqlalchemy import func

def get_products_for_sale(db: Session, search: str = None, cart_session_id: str = None, only_available: bool = False):
    #Subconsulta para obtener la cantidad reservada por otros carritos activos
    reserved_subquery = (
        db.query(
            InventoryReservation.id_product,
            func.sum(InventoryReservation.quantity).label("reserved_qty")
        )
        .filter(InventoryReservation.expires_at > datetime.utcnow())
    )
    
    if cart_session_id:
        reserved_subquery = reserved_subquery.filter(
            InventoryReservation.cart_session_id != cart_session_id
        )
        
    reserved_subquery = reserved_subquery.group_by(InventoryReservation.id_product).subquery()

    query = db.query(
        Product.id_product,
        Product.name,
        Category.name.label("category_name"),
        Product.sale_price,
        Product.stock,
        Product.minimum_stock,
        func.coalesce(reserved_subquery.c.reserved_qty, 0).label("reserved")
    ).join(Category, Product.id_category == Category.id_category)\
    .outerjoin(reserved_subquery, Product.id_product == reserved_subquery.c.id_product)\
    .filter(Product.active == True)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Category.name.ilike(search_filter)
            )
        )
    
    products_data = query.all()

    result = []
    for p in products_data:
        available_stock = p.stock - p.reserved
        
        #Filtro de productos sin stock disponible
        if only_available and available_stock <= 0:
            continue
            
        result.append({
            "id_product": p.id_product,
            "name": p.name,
            "category_name": p.category_name,
            "sale_price": p.sale_price,
            "stock": available_stock,
            "minimum_stock": p.minimum_stock
        })

    return {
        "total": len(result),
        "data": result
    }


def get_all_products_for_report(db: Session, category_id: int = None, active: bool = None):
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.deleted_at == None)

    if category_id is not None:
        query = query.filter(Product.id_category == category_id)

    if active is not None:
        query = query.filter(Product.active == active)

    return query.all()


def get_all_active_products(db: Session):
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.deleted_at == None, Product.active == True, Product.stock > 0)
        .all()
    )


'''def get_products(db: Session, page: int = 1, limit: int = 10, category_id: int = None, active: bool = None, search: str = None, category_name: str = None, status: str = None):
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.deleted_at == None)

    if category_id is not None:
        query = query.filter(Product.id_category == category_id)
    
    if category_name:
        query = query.join(Product.category).filter(Category.name == category_name)

    if active is not None:
        query = query.filter(Product.active == active)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Product.sku.ilike(search_filter),
                Category.name.ilike(search_filter)
            )
        )

    if status == "Agotado":
        query = query.filter(Product.stock == 0)
    elif status == "Stock crítico":
        query = query.filter(Product.stock > 0, Product.stock <= Product.minimum_stock)
    elif status == "Disponible":
        query = query.filter(Product.stock > Product.minimum_stock)

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return {"data": products, "total": total, "page": page, "limit": limit}'''


def get_products(db: Session, page: int = 1, limit: int = 10, category_id: int = None, active: bool = None, search: str = None, category_name: str = None, status: str = None):
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.deleted_at == None)

    if category_id is not None:
        query = query.filter(Product.id_category == category_id)

    needs_category_join = category_name or (search and True)
    if needs_category_join:
        query = query.join(Product.category)

    if category_name:
        query = query.filter(Category.name == category_name)

    if active is not None:
        query = query.filter(Product.active == active)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Product.sku.ilike(search_filter),
                Category.name.ilike(search_filter)
            )
        )

    if status == "Agotado":
        query = query.filter(Product.stock == 0)
    elif status == "Stock crítico":
        query = query.filter(Product.stock > 0, Product.stock <= Product.minimum_stock)
    elif status == "Disponible":
        query = query.filter(Product.stock > Product.minimum_stock)

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return {"data": products, "total": total, "page": page, "limit": limit}


def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id_product == product_id, Product.deleted_at == None)
        .first()
    )


def generate_sku() -> str:
    return f"{uuid.uuid4().hex[:8].upper()}"


def create_product(db: Session, product_data: ProductCreate):
    new_product = Product(
        **product_data.dict(),
        sku=generate_sku()
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return get_product_by_id(db, new_product.id_product)


def update_product(db: Session, product: Product, updates: ProductUpdate):
    update_data = updates.dict(exclude_unset=True)

    # Verificar SKU duplicado si se está cambiando
    if "sku" in update_data:
        existing = (
            db.query(Product)
            .filter(Product.sku == update_data["sku"], Product.id_product != product.id_product)
            .first()
        )
        if existing:
            raise ValueError("El SKU ya está registrado")

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return get_product_by_id(db, product.id_product)

def delete_product(db: Session, product: Product):
    # Verificar si tiene ventas o movimientos de inventario asociados
    has_sales = len(product.sale_details) > 0
    has_movements = len(product.inventory_movements) > 0

    if has_sales or has_movements:
        raise ValueError(
            "Este producto tiene ventas o movimientos de inventario registrados y no puede eliminarse. "
            "Si deseas retirarlo del catálogo, desactívalo."
        )

    product.deleted_at = datetime.utcnow()
    db.commit()
