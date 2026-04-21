from sqlalchemy.orm import Session
from app.models.category import Category, CategoryStatus


def get_categories(db: Session):
    return (
        db.query(Category)
        .filter(Category.status == CategoryStatus.ACTIVE)
        .all()
    )