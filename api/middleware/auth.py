"""Authentication middleware for the API."""
from functools import wraps
from flask import request, jsonify
from api.config.config import Config

def require_api_key(f):
    """Decorator to require API key for route access.
    
    Args:
        f: Function to wrap
        
    Returns:
        Function: Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if key and key == Config.API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated
