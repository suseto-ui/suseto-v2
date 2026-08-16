from functools import wraps
from flask import jsonify
from flask_login import current_user

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"status": "error", "message": "Neautorizovaný přístup"}), 401
            
            user_role = current_user.role
            has_access = False
            
            if required_role == 'admin' and user_role in ['admin', 'superadmin']:
                has_access = True
            elif required_role == 'superadmin' and user_role == 'superadmin':
                has_access = True
                
            if not has_access:
                return jsonify({"status": "error", "message": "Nedostatečná oprávnění"}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
