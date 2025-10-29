from datetime import datetime
from bson import ObjectId

class EvidenceModel:
    @staticmethod
    def collection():
        from app import mongo
        return mongo.db.evidences

    @staticmethod
    def add(incident_id, filename, url, uploaded_by):
        col = EvidenceModel.collection()
        doc = {
            "incident_id": incident_id,
            "filename": filename,
            "url": url,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.utcnow()
        }
        res = col.insert_one(doc)
        return str(res.inserted_id)

    @staticmethod
    def list_all(incident_id=None, limit=500):
        col = EvidenceModel.collection()
        query = {}
        if incident_id:
            query["incident_id"] = incident_id
        docs = col.find(query).sort("uploaded_at", -1).limit(limit)
        result = []
        for d in docs:
            d["_id"] = str(d["_id"])
            result.append(d)
        return result

    @staticmethod
    def delete(evidence_id):
        col = EvidenceModel.collection()
        try:
            oid = ObjectId(evidence_id)
        except Exception:
            return False
        res = col.delete_one({"_id": oid})
        return res.deleted_count > 0
