from datetime import datetime
from bson import ObjectId

class IncidentModel:
    @staticmethod
    def collection():
        from app import mongo
        return mongo.db.incidents

    @staticmethod
    def create(title, description, category, severity, created_by):
        col = IncidentModel.collection()
        doc = {
            "title": title,
            "description": description,
            "category": category,
            "severity": severity,
            "status": "open",
            "created_by": created_by,
            "assigned_to": None,
            "created_at": datetime.utcnow(),
            "history": []
        }
        res = col.insert_one(doc)
        return str(res.inserted_id)

    @staticmethod
    def get_by_id(oid_str):
        col = IncidentModel.collection()
        try:
            oid = ObjectId(oid_str)
        except Exception:
            return None
        doc = col.find_one({"_id": oid})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def list_all(limit=500, filters=None):
        col = IncidentModel.collection()
        query = filters or {}
        docs = col.find(query).sort("created_at", -1).limit(limit)
        result = []
        for d in docs:
            d["_id"] = str(d["_id"])
            result.append(d)
        return result

    @staticmethod
    def update(oid_str, updates, actor=None, note=None):
        col = IncidentModel.collection()
        try:
            oid = ObjectId(oid_str)
        except Exception:
            return False
        update_doc = {"$set": updates}
        if actor or note:
            event = {"actor": actor, "action": "update", "date": datetime.utcnow(), "note": note}
            update_doc["$push"] = {"history": event}
        res = col.update_one({"_id": oid}, update_doc)
        return res.matched_count > 0

    @staticmethod
    def delete(oid_str):
        col = IncidentModel.collection()
        try:
            oid = ObjectId(oid_str)
        except Exception:
            return False
        res = col.delete_one({"_id": oid})
        return res.deleted_count > 0

    @staticmethod
    def assign(oid_str, username, actor=None):
        return IncidentModel.update(oid_str, {"assigned_to": username}, actor=actor, note=f"Asignado a {username}")

    @staticmethod
    def change_status(oid_str, new_status, actor=None, note=None):
        return IncidentModel.update(oid_str, {"status": new_status}, actor=actor, note=note)
