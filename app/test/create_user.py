import app.models.category
import app.models.detail_sale
import app.models.generated_report
import app.models.inventory_movement
import app.models.product
import app.models.sale

from app.db.database import SessionLocal
from app.models.role import Role
from app.models.user import User, UserStatus
from app.utils.security import hash_password


USERS = [
    {
        "role_name":  "Administrador",
        "first_name": "Admin",
        "last_name":  "Prueba",
        "email":      "admin@farmauady.com",
        "password":   "Admin1234!",
    },
    {
        "role_name":  "Vendedor",
        "first_name": "Vendedor",
        "last_name":  "Prueba",
        "email":      "vendedor@farmauady.com",
        "password":   "Vendedor1234!",
    },
]


def get_or_create_role(db, role_name: str) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.flush()
        print(f"Rol creado: '{role_name}'")
    else:
        print(f"Rol ya existe: '{role_name}' (id={role.id_role})")
    return role


def create_test_users():
    db = SessionLocal()
    try:
        for data in USERS:
            print(f"\n--- Procesando usuario: {data['email']}")

            existing = db.query(User).filter(User.email == data["email"]).first()
            if existing:
                print(f"Usuario ya existe, se omite.")
                continue

            role = get_or_create_role(db, data["role_name"])

            user = User(
                id_role=role.id_role,
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password_hash=hash_password(data["password"]),
                status=UserStatus.ACTIVE,
            )
            db.add(user)
            db.flush()
            print(f"Usuario creado: {user.first_name} {user.last_name} "
                  f"email={user.email} | rol={data['role_name']}")

        db.commit()
        print("Todos los usuarios de prueba fueron guardados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"Error al crear usuarios: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
