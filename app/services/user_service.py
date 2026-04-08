from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from datetime import datetime
from sqlalchemy.orm import joinedload
import bcrypt

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode() 


def create_user(db: Session, user_data: UserCreate):
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


def get_users(db: Session):
    return db.query(User).options(joinedload(User.role)).filter(User.deleted_at == None).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(
        User.id_user == user_id,
        User.deleted_at == None
    ).first()


def update_user(db: Session, user, updates: UserUpdate):
    update_data = updates.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user):
    user.deleted_at = datetime.utcnow()
    db.commit()