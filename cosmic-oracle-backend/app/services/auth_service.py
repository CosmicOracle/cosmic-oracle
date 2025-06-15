# app/services/auth_service.py
"""
Authentication Service

Handles password verification and JWT token creation. Contains no DB logic.
"""
import logging
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """A singleton service for security-related operations."""
    _instance = None
    
    def __init__(self):
        logger.info("Initializing AuthService singleton...")
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        logger.info("AuthService initialized successfully.")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed one."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Creates a new JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

try:
    auth_service_instance = AuthService()
except Exception as e:
    logger.critical(f"Could not instantiate AuthService: {e}")
    auth_service_instance = None