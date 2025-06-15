# app/utils/auth_utils.py
"""
Authentication utilities for handling JWT tokens and user authentication
"""
import logging
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

def get_current_user_id():
    """
    Get the current authenticated user ID from JWT token.
    Returns None if no valid token is present.
    """
    try:
        # Verify JWT token is present and valid
        verify_jwt_in_request()
        # Get user identity from token
        user_id = get_jwt_identity()
        if user_id:
            return int(user_id)
        return None
    except Exception as e:
        logger.warning(f"Failed to get current user ID: {e}")
        return None

def require_auth(f):
    """
    Decorator to require authentication for API endpoints.
    Returns 401 if no valid token is present.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_current_user_id()
            if not user_id:
                return jsonify({"message": "Authentication required"}), 401
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({"message": "Authentication failed"}), 401
    return decorated_function

def optional_auth(f):
    """
    Decorator for endpoints that work with or without authentication.
    Sets user_id to None if no valid token is present.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Try to get user ID, but don't fail if not present
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user_id = int(user_id)
        except:
            user_id = None
        
        # Pass user_id as first argument to the function
        return f(user_id, *args, **kwargs)
    return decorated_function

def get_user_from_token():
    """
    Extract user information from JWT token.
    Returns user data dict or None if invalid.
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if user_id:
            # Here you could fetch additional user data from database
            # For now, just return basic info
            return {
                'id': int(user_id),
                'authenticated': True
            }
        return None
    except Exception as e:
        logger.debug(f"Token validation failed: {e}")
        return None
