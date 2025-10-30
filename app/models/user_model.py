from bson import ObjectId
from flask_login import UserMixin

from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.role = user_data.get("role", "user")
        self.fullname = user_data.get("fullname", "")
        self.phone = user_data.get("phone", "")

class UserModel:
    @staticmethod
    def collection():
        from app import mongo

        return mongo.db.users

    @staticmethod
    def create_user(username, email, password, fullname, phone, role):
        from app import mongo, bcrypt 
        col = UserModel.collection()

        if col.find_one({"username": username}):
            return False, "El usuario ya existe."
        if col.find_one({"email": email}):
            return False, "El correo ya está registrado."

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw,
            "role": role, 
            "fullname": fullname,
            "phone": phone,
            "creation_date": datetime.utcnow()
        })
        return True, "Usuario creado exitosamente."

    @staticmethod
    def verify_user(username, password):
        from app import bcrypt
        col = UserModel.collection()
        user = col.find_one({"username": username})
        if not user:
            return False, None
        if bcrypt.check_password_hash(user["password"], password):
            return True, {
                "_id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "role": user.get("role", "user"),
                "fullname": user.get("fullname", ""),
                "phone": user.get("phone", ""),
                "created_at": user.get("created_at")
            }
        return False, None
    
    @staticmethod
    def get_by_username(username):
        col = UserModel.collection()
        user = col.find_one({"username": username}, {"password": 0})
        if user:
            user["_id"] = str(user["_id"])
        return user

    @staticmethod
    def get_by_id(id_str):
        col = UserModel.collection()
        try:
            oid = ObjectId(id_str)
        except Exception:
            return None
        user = col.find_one({"_id": oid}, {"password": 0})
        if user:
            user["_id"] = str(user["_id"])
        return user

    @staticmethod
    def list_users(limit = 200):
        col = UserModel.collection()
        docs = col.find({}, {"password": 0}).sort("created_at", -1).limit(limit)
        results = []
        for u in docs:
            u["_id"] = str(u["_id"])
            results.append(u)
        return results

    @staticmethod
    def change_role(username, new_rolee):
        col = UserModel.collection()
        if new_rolee not in ["admin", "analyst", "user"]:
            return False, "Rol inválido."
        result = col.update_one({"username": username}, {"$set": {"role": new_rolee}})
        if result.matched_count:
            return True, "Rol actualizado correctamente."
        return False, "Usuario no encontrado."