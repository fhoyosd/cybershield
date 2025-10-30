from flask import Flask

from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from app.models.user_model import UserModel

from .config import Config

from .routes.auth_routes import auth_bp
from .routes.main_routes import main_bp
from .routes.admin_routes import admin_bp

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
    login_manager.login_message_category = "info"

    from app.models.user_model import UserModel

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.get_by_id(user_id)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    try:
        mongo.cx.server_info()
        print("Conectado correctamente a MongoDB")
    except Exception as e:
        print("Error al conectar con MongoDB:", e)

    return app