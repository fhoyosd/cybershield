import requests

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user, login_required

from app.models.user_model import UserModel

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        recaptcha_response = request.form.get("g-recaptcha-response")
        secret = current_app.config["RECAPTCHA_SECRET_KEY"]

        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {"secret": secret, "response": recaptcha_response}
        result = requests.post(verify_url, data=payload).json()

        if not result.get("success"):
            flash("Verifica el reCAPTCHA antes de continuar.", "error")
            return redirect(request.url)

        username = request.form.get("username")
        password = request.form.get("password")

        valid, user_obj = UserModel.verify_user(username, password)
        if valid:
            login_user(user_obj)
            flash("Inicio de sesión exitoso.", "success")

            if user_obj.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user_obj.role == "analyst":
                return redirect(url_for("analyst.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))

        flash("Usuario o contraseña incorrectos.", "danger")
        return redirect(url_for("auth.login"))

    site_key = current_app.config["RECAPTCHA_SITE_KEY"]
    return render_template("auth/login.html", site_key=site_key)

@auth_bp.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        recaptcha_response = request.form.get('g-recaptcha-response')
        secret = current_app.config['RECAPTCHA_SECRET_KEY']

        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {"secret": secret, "response": recaptcha_response}
        r = requests.post(verify_url, data = payload)
        result = r.json()

        if not result.get("success"):
            flash("Verifica el reCAPTCHA antes de continuar.", "error")
            return redirect(request.url)

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        fullname = request.form.get("fullname")
        phone = request.form.get("phone")

        if password != confirm:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("auth.register"))

        success, message = UserModel.create_user(
            username = username, 
            email = email, 
            password = password, 
            fullname = fullname, 
            phone = phone, 
            role = "user"
        )
        flash(message, "success" if success else "error")

        return redirect(url_for('auth.login') if success else url_for('auth.register'))

    site_key = current_app.config['RECAPTCHA_SITE_KEY']
    return render_template('auth/register.html', site_key = site_key)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))
