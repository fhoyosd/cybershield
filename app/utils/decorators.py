from functools import wraps
from flask import session, redirect, url_for, flash
from app.models.user_model import UserModel

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Debes iniciar sesión primero.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                flash('Debes iniciar sesión primero.', 'error')
                return redirect(url_for('auth.login'))

            user = UserModel.get_by_username(session['username'])
            if not user:
                flash('Usuario no encontrado.', 'error')
                return redirect(url_for('auth.login'))

            if user.get('role') not in roles:
                flash('No tienes permiso para acceder a esta área.', 'error')
                return redirect(url_for('main.home'))

            return f(*args, **kwargs)
        return wrapper
    return decorator
