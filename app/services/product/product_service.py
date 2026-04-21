import uuid
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_products(db: Session):
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.deleted_at == None)
        .all()
    )


def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id_product == product_id, Product.deleted_at == None)
        .first()
    )

def generate_sku() -> str:
    return f"SKU-{uuid.uuid4().hex[:8].upper()}"


"""def create_product(db: Session, product_data: ProductCreate):
    # Verificar SKU duplicado
    existing = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing:
        raise ValueError("El SKU ya está registrado")

    new_product = Product(
        **product_data.dict(),
        sku=generate_sku()
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Recargar con relaciones
    return get_product_by_id(db, new_product.id_product)"""

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


#def delete_product(db: Session, product: Product):
#    product.deleted_at = datetime.utcnow()
#    db.commit()

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