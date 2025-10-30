from bson import ObjectId
from datetime import datetime

from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.role = user_data.get("role", "user")
        self.fullname = user_data.get("fullname", "")
        self.phone = user_data.get("phone", "")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "fullname": self.fullname,
            "phone": self.phone,
        }

class UserModel:
    @staticmethod
    def collection():
        from app import mongo
        return mongo.db.users

    @staticmethod
    def create_user(username, email, password, fullname, phone, role):
        from app import bcrypt
        col = UserModel.collection()

        if col.find_one({"username": username}):
            return False, "El usuario ya existe."
        if col.find_one({"email": email}):
            return False, "El correo ya está registrado."

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_pw,
            "role": role,
            "fullname": fullname,
            "phone": phone,
            "created_at": datetime.utcnow(),
        }

        col.insert_one(user_doc)
        return True, "Usuario creado exitosamente."

    @staticmethod
    def verify_user(username, password):
        """Verifies credentials and returns a User instance if valid."""
        from app import bcrypt
        col = UserModel.collection()

        user_data = col.find_one({"username": username})
        if not user_data:
            return False, None

        if bcrypt.check_password_hash(user_data["password"], password):
            return True, User(user_data)

        return False, None

    @staticmethod
    def get_by_username(username):
        col = UserModel.collection()
        user_data = col.find_one({"username": username}, {"password": 0})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_id(user_id):
        col = UserModel.collection()
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None

        user_data = col.find_one({"_id": oid})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def list_users(limit=200):
        col = UserModel.collection()
        docs = col.find({}, {"password": 0}).sort("created_at", -1).limit(limit)
        return [{**u, "_id": str(u["_id"])} for u in docs]

    @staticmethod
    def change_role(username, new_role):
        """Updates the user's role."""
        col = UserModel.collection()

        if new_role not in ["admin", "analyst", "user"]:
            return False, "Rol inválido."

        result = col.update_one({"username": username}, {"$set": {"role": new_role}})
        if result.matched_count:
            return True, "Rol actualizado correctamente."
        return False, "Usuario no encontrado."
