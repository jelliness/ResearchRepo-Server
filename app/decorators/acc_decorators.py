from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from flask import jsonify

def roles_required(allowed_roles):
    """
    A decorator that checks if the user has one of the allowed roles.
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()  # Get the claims from the token
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify({"message": "Access forbidden: insufficient role"}), 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator