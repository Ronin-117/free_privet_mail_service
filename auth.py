"""
Authentication module for JWT-based authentication.

Author: AI Assistant
Created: 2025-12-02
"""

from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from utils import error_response


def jwt_required_custom(fn):
    """
    Custom JWT required decorator with better error handling.
    
    Args:
        fn: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return error_response('Authentication required', 401)
    return wrapper


def get_current_user():
    """
    Get the current authenticated user's identity.
    
    Returns:
        User identity from JWT token
    """
    try:
        return get_jwt_identity()
    except:
        return None
