from flask import Blueprint, render_template, request, redirect, url_for, flash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        print(f"Intento de login - Usuario: {username}, Contraseña: {password}")
        flash("Función de login aún no implementada.", "info")

        return redirect(url_for("auth.login"))
    
    return render_template("login.html")

@auth_bp.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        print(f"Registro - Usuario: {username}, Email: {email}")
        flash("Registro simulado. (Aún no conectado a la base de datos)", "info")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/forgot-password")
def forgot_password():
    return "<h2>Funcionalidad de recuperación de contraseña próximamente</h2>"
