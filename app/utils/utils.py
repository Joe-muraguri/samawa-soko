from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity or identity.get('role') != required_role:
                return jsonify({"Error":"Unauthorized"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

