from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.utils.validate_password import validate_password
from datetime import datetime
from sqlalchemy.orm import joinedload
import bcrypt


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode() 


def create_user(db: Session, user_data: UserCreate):
    # validar contraseña
    validate_password(user_data.password)

    # verificar email duplicado
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValueError("Email ya registrado")

    new_user = User(
        id_role=user_data.id_role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        status=user_data.status
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


'''def get_users(db: Session, page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    total = db.query(User).filter(User.deleted_at == None).count()
    users = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.deleted_at == None)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"data": users, "total": total, "page": page, "limit": limit}'''


def get_users(db: Session, page: int = 1, limit: int = 10, search: str = None):
    query = db.query(User).options(joinedload(User.role)).filter(User.deleted_at == None)

    if search:
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    return {"data": users, "total": total, "page": page, "limit": limit}


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(
        User.id_user == user_id,
        User.deleted_at == None
    ).first()


def get_sellers(db: Session):
    return (
        db.query(User)
        .options(joinedload(User.role))
        .join(User.role)
        .filter(User.deleted_at == None, Role.name == "Vendedor")
        .all()
    )


def update_user(db: Session, user, updates: UserUpdate):
    update_data = updates.dict(exclude_unset=True)

    if "password" in update_data:
        validate_password(update_data["password"])
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user, current_user):
    # No puede eliminarse a sí mismo
    if user.id_user == current_user.id_user:
        raise ValueError("No puedes eliminar tu propia cuenta")

    # Solo puede eliminar vendedores
    if user.role.name != "Vendedor":
        raise ValueError("Solo puedes eliminar usuarios con rol Vendedor")

    user.deleted_at = datetime.utcnow()
    db.commit()