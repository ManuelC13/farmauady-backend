from sqlalchemy.orm import Session
from app.models.category import Category, CategoryStatus
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_categories(db: Session):
    return (
        db.query(Category)
        .filter(Category.status == CategoryStatus.ACTIVE)
        .all()
    )


def get_category_by_id(db: Session, category_id: int):
    return db.query(Category).filter(
        Category.id_category == category_id,
        Category.status == CategoryStatus.ACTIVE
    ).first()


def create_category(db: Session, data: CategoryCreate):
    # Verificar nombre duplicado
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise ValueError("Ya existe una categoría con ese nombre")

    category = Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, data: CategoryUpdate):
    # Verificar nombre duplicado excluyendo la categoría actual
    existing = db.query(Category).filter(
        Category.name == data.name,
        Category.id_category != category.id_category
    ).first()
    if existing:
        raise ValueError("Ya existe una categoría con ese nombre")

    category.name = data.name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category):
    # Verificar si tiene productos activos asociados
    has_products = any(
        p.deleted_at is None for p in category.products
    )
    if has_products:
        raise ValueError(
            "Esta categoría tiene productos activos y no puede desactivarse. "
            "Reasigna los productos primero."
        )

    category.status = CategoryStatus.INACTIVE
    db.commit()