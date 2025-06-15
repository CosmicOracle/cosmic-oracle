# app/repositories/user_repository.py
"""
Repository for all User model database operations.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.models.orm_models import User
from passlib.context import CryptContext

# It's good practice for the repository to handle the password context
# if it's the one creating/updating the user record with the hash.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    """Hashes a plain text password."""
    return pwd_context.hash(password)

def find_by_id(db: Session, user_id: int) -> Optional[User]:
    """Finds a user by their primary key ID."""
    return db.query(User).filter(User.id == user_id).first()

def find_by_email(db: Session, email: str) -> Optional[User]:
    """Finds a user by their email address."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, full_name: str, email: str, password: str) -> User:
    """Creates a new user record in the database with a hashed password."""
    hashed_password = get_hashed_password(password)
    new_user = User(
        full_name=full_name,
        email=email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user: User, update_data: Dict[str, Any]) -> User:
    """Updates a user's details."""
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User):
    """Deletes a user record."""
    db.delete(user)
    db.commit()