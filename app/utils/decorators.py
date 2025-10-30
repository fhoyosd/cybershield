from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import current_user, login_required

from app.models.user_model import UserModel

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator