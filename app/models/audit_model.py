from datetime import datetime

class AuditModel:
    @staticmethod
    def collection():
        from app import mongo
        return mongo.db.audits

    @staticmethod
    def log(actor, action, target_type=None, target_id=None, detail=None):
        col = AuditModel.collection()
        entry = {
            "actor": actor,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "detail": detail,
            "timestamp": datetime.utcnow()
        }
        col.insert_one(entry)

    @staticmethod
    def list_all(limit=500, filters=None):
        col = AuditModel.collection()
        query = filters or {}
        docs = col.find(query).sort("timestamp", -1).limit(limit)
        result = []
        for d in docs:
            d["_id"] = str(d["_id"])
            result.append(d)
        return result
