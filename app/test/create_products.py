import app.models.category
import app.models.detail_sale
import app.models.generated_report
import app.models.inventory_movement
import app.models.product
import app.models.role
import app.models.sale
import app.models.user

from datetime import date
from app.db.database import SessionLocal
from app.models.category import Category, CategoryStatus
from app.models.product import Product

CATEGORIES = ["Medicamentos", "Cuidado Personal", "Suplementos"]

PRODUCTS = [
    {
        "category_name": "Medicamentos",
        "name": "Paracetamol 500mg",
        "description": "Analgésico y antipirético",
        "sku": "MED-001",
        "sale_price": 50.00,
        "stock": 100,
        "minimum_stock": 20,
        "expiration_date": date(2025, 12, 31),
        "batch": "LOT123"
    },
    {
        "category_name": "Medicamentos",
        "name": "Ibuprofeno 400mg",
        "description": "Antiinflamatorio no esteroideo",
        "sku": "MED-002",
        "sale_price": 75.00,
        "stock": 80,
        "minimum_stock": 15,
        "expiration_date": date(2025, 6, 30),
        "batch": "LOT456"
    },
    {
        "category_name": "Cuidado Personal",
        "name": "Jabón Líquido Antibacterial",
        "description": "Para manos, 500ml",
        "sku": "CP-001",
        "sale_price": 45.00,
        "stock": 50,
        "minimum_stock": 10,
        "expiration_date": date(2026, 1, 1),
        "batch": "LOT789"
    },
    {
        "category_name": "Suplementos",
        "name": "Vitamina C 1g",
        "description": "Suplemento alimenticio efervescente",
        "sku": "SUP-001",
        "sale_price": 120.00,
        "stock": 30,
        "minimum_stock": 5,
        "expiration_date": date(2025, 8, 15),
        "batch": "LOT012"
    }
]

def get_or_create_category(db, category_name: str) -> Category:
    category = db.query(Category).filter(Category.name == category_name).first()
    if not category:
        category = Category(name=category_name, status=CategoryStatus.ACTIVE)
        db.add(category)
        db.flush()
        print(f"Categoría creada: '{category_name}'")
    else:
        print(f"Categoría ya existe: '{category_name}' (id={category.id_category})")
    return category

def create_test_products():
    db = SessionLocal()
    try:
        category_map = {}
        for cat_name in CATEGORIES:
            cat = get_or_create_category(db, cat_name)
            category_map[cat_name] = cat.id_category

        for data in PRODUCTS:
            print(f"\n--- Procesando producto: {data['name']} ({data['sku']})")

            existing = db.query(Product).filter(Product.sku == data["sku"]).first()
            if existing:
                print(f"Producto con SKU '{data['sku']}' ya existe, se omite.")
                continue

            id_category = category_map.get(data["category_name"])
            if not id_category:
                print(f"Error: Categoría '{data['category_name']}' no encontrada para el producto {data['name']}")
                continue

            product = Product(
                id_category=id_category,
                name=data["name"],
                description=data["description"],
                sku=data["sku"],
                sale_price=data["sale_price"],
                stock=data["stock"],
                minimum_stock=data["minimum_stock"],
                expiration_date=data["expiration_date"],
                batch=data["batch"],
                active=True
            )
            db.add(product)
            db.flush()
            print(f"Producto creado: {product.name} | SKU={product.sku}")

        db.commit()
        print("\nTodos los productos de prueba fueron guardados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"Error al crear productos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_products()
