# app/services/user_service.py
"""
User Management Service

Orchestrates user creation, updates, and data retrieval by interacting
with the user repository and authentication service.
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories import user_repository
from app.services.auth_service import auth_service_instance

logger = logging.getLogger(__name__)

class UserService:
    """A singleton service for user-related business logic."""
    _instance = None

    def create_new_user(self, db: Session, full_name: str, email: str, password: str) -> Dict[str, Any]:
        """Business logic for creating a new user."""
        logger.info(f"Attempting to create new user with email: {email}")
        existing_user = user_repository.find_by_email(db, email)
        if existing_user:
            return {"error": "An account with this email address already exists."}
        
        try:
            new_user = user_repository.create_user(db, full_name, email, password)
            # Exclude password hash from the response
            return {"message": "User created successfully.", "user_id": new_user.id, "email": new_user.email}
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}", exc_info=True)
            return {"error": "An internal error occurred during user creation."}
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates a user and returns user data if successful."""
        user = user_repository.find_by_email(db, email)
        if not user or not auth_service_instance.verify_password(password, user.hashed_password):
            return None # Authentication failed
        
        # Return user object for token creation
        return {"id": user.id, "email": user.email, "full_name": user.full_name}

    def get_user_profile(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a user's public-safe profile information."""
        user = user_repository.find_by_id(db, user_id)
        if not user:
            return None
        return {
            "id": user.id, "full_name": user.full_name, "email": user.email,
            "is_active": user.is_active, "created_at": user.created_at.isoformat()
        }

try:
    user_service_instance = UserService()
except Exception as e:
    logger.critical(f"Could not instantiate UserService: {e}")
    user_service_instance = None