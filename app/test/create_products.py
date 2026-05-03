import app.models.category
import app.models.detail_sale
import app.models.generated_report
import app.models.inventory_movement
import app.models.product
import app.models.role
import app.models.sale
import app.models.user

from datetime import date, timedelta
import random
from app.db.database import SessionLocal
from app.models.category import Category, CategoryStatus
from app.models.product import Product

CATEGORIES = ["Medicamentos", "Cuidado Personal", "Suplementos", "Higiene", "Infantil"]

# Listas para generar nombres realistas
MEDS = ["Paracetamol", "Ibuprofeno", "Amoxicilina", "Loratadina", "Omeprazol", "Metformina", "Enalapril", "Atorvastatina", "Salbutamol", "Naproxeno"]
CP = ["Shampoo", "Acondicionador", "Crema Corporal", "Desodorante", "Pasta Dental", "Enjuague Bucal", "Protector Solar", "Jabón de Barra"]
SUP = ["Vitamina C", "Multivitamínico", "Omega 3", "Colágeno", "Magnesio", "Zinc", "Proteína Whey", "B-Complex"]
HIG = ["Toallitas Húmedas", "Gel Antibacterial", "Alcohol Isopropílico", "Algodón", "Gasas Estériles"]
INF = ["Pañales Etapa 1", "Fórmula Infantil", "Biberón 8oz", "Chupón Silicona", "Talco para Bebé"]

def generate_50_products():
    products = []
    
    # 1. Medicamentos (20)
    for i in range(20):
        name = random.choice(MEDS) + " " + random.choice(["500mg", "1g", "250mg", "5mg", "10mg"])
        products.append({
            "category_name": "Medicamentos",
            "name": name,
            "description": f"Tratamiento farmacéutico de alta calidad - {name}",
            "sku": f"MED-{100 + i}",
            "sale_price": round(random.uniform(15.0, 450.0), 2),
            "stock": random.randint(10, 200),
            "minimum_stock": random.randint(5, 20),
            "expiration_date": date.today() + timedelta(days=random.randint(365, 1000)),
            "batch": f"LOT-M{random.randint(1000, 9999)}"
        })

    # 2. Cuidado Personal (10)
    for i in range(10):
        name = random.choice(CP) + " " + random.choice(["Premium", "Naturals", "Pro", "Fresh"])
        products.append({
            "category_name": "Cuidado Personal",
            "name": name,
            "description": f"Cuidado y belleza para toda la familia - {name}",
            "sku": f"CP-{100 + i}",
            "sale_price": round(random.uniform(35.0, 150.0), 2),
            "stock": random.randint(20, 100),
            "minimum_stock": random.randint(5, 15),
            "expiration_date": date.today() + timedelta(days=random.randint(500, 1200)),
            "batch": f"LOT-C{random.randint(1000, 9999)}"
        })

    # 3. Suplementos (10)
    for i in range(10):
        name = random.choice(SUP) + " " + random.choice(["Forte", "Max", "Advanced", "Plus"])
        products.append({
            "category_name": "Suplementos",
            "name": name,
            "description": f"Refuerza tu salud nutricional - {name}",
            "sku": f"SUP-{100 + i}",
            "sale_price": round(random.uniform(80.0, 600.0), 2),
            "stock": random.randint(5, 50),
            "minimum_stock": random.randint(2, 10),
            "expiration_date": date.today() + timedelta(days=random.randint(400, 800)),
            "batch": f"LOT-S{random.randint(1000, 9999)}"
        })

    # 4. Higiene (5)
    for i in range(5):
        name = random.choice(HIG)
        products.append({
            "category_name": "Higiene",
            "name": name,
            "description": f"Limpieza y desinfección profunda - {name}",
            "sku": f"HIG-{100 + i}",
            "sale_price": round(random.uniform(20.0, 80.0), 2),
            "stock": random.randint(50, 300),
            "minimum_stock": random.randint(20, 50),
            "expiration_date": date.today() + timedelta(days=random.randint(300, 900)),
            "batch": f"LOT-H{random.randint(1000, 9999)}"
        })

    # 5. Infantil (5)
    for i in range(5):
        name = random.choice(INF)
        products.append({
            "category_name": "Infantil",
            "name": name,
            "description": f"Lo mejor para el cuidado del bebé - {name}",
            "sku": f"INF-{100 + i}",
            "sale_price": round(random.uniform(50.0, 350.0), 2),
            "stock": random.randint(15, 80),
            "minimum_stock": random.randint(5, 15),
            "expiration_date": date.today() + timedelta(days=random.randint(400, 1000)),
            "batch": f"LOT-I{random.randint(1000, 9999)}"
        })

    return products

PRODUCTS = generate_50_products()

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
        print(f"\n{len(PRODUCTS)} productos de prueba fueron procesados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"Error al crear productos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_products()
