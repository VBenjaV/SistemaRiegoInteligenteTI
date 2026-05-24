import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from bson import ObjectId

from app.db.mongo import get_lecturas_collection
from app.models import LecturaSensorCreate

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _doc_to_dict(doc: dict) -> dict:
    """Convertir documento MongoDB a dict compatible con Pydantic."""
    result = {
        "id": str(doc["_id"]),
        "dispositivo_id": doc["dispositivo_id"],
        "humedad": doc["humedad"],
        "temperatura": doc.get("temperatura"),
        "timestamp": doc["timestamp"],
        "creado": doc.get("creado", doc["timestamp"]),
        "topic": doc.get("topic"),
        "payload_raw": doc.get("payload_raw"),
    }
    return result


class MongoSensorService:
    """Persistencia de lecturas de sensores en MongoDB."""

    @staticmethod
    def crear_lectura(
        lectura: LecturaSensorCreate,
        topic: Optional[str] = None,
        payload_raw: Optional[str] = None,
    ) -> dict:
        ts = lectura.timestamp or _utcnow()
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        doc = {
            "dispositivo_id": lectura.dispositivo_id,
            "humedad": lectura.humedad,
            "temperatura": lectura.temperatura,
            "timestamp": ts,
            "creado": _utcnow(),
            "topic": topic,
            "payload_raw": payload_raw,
        }
        result = get_lecturas_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        logger.info(
            "Lectura MongoDB: humedad=%.1f%% dispositivo=%s",
            lectura.humedad,
            lectura.dispositivo_id,
        )
        return _doc_to_dict(doc)

    @staticmethod
    def obtener_ultima_lectura(dispositivo_id: str) -> Optional[dict]:
        doc = get_lecturas_collection().find_one(
            {"dispositivo_id": dispositivo_id},
            sort=[("timestamp", -1)],
        )
        return _doc_to_dict(doc) if doc else None

    @staticmethod
    def obtener_historial(
        dispositivo_id: str,
        limit: int = 100,
        offset: int = 0,
        inicio: Optional[datetime] = None,
        fin: Optional[datetime] = None,
    ) -> tuple[list[dict], int]:
        query: dict[str, Any] = {"dispositivo_id": dispositivo_id}
        if inicio or fin:
            ts_filter: dict[str, Any] = {}
            if inicio:
                ts_filter["$gte"] = inicio
            if fin:
                ts_filter["$lte"] = fin
            query["timestamp"] = ts_filter

        collection = get_lecturas_collection()
        total = collection.count_documents(query)
        cursor = (
            collection.find(query)
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )
        return [_doc_to_dict(doc) for doc in cursor], total

    @staticmethod
    def obtener_promedio_humedad(
        dispositivo_id: str,
        minutos: int = 60,
    ) -> Optional[float]:
        limite = _utcnow() - timedelta(minutes=minutos)
        pipeline = [
            {
                "$match": {
                    "dispositivo_id": dispositivo_id,
                    "timestamp": {"$gte": limite},
                }
            },
            {"$group": {"_id": None, "promedio": {"$avg": "$humedad"}}},
        ]
        result = list(get_lecturas_collection().aggregate(pipeline))
        if not result:
            return None
        return result[0]["promedio"]

    @staticmethod
    def obtener_por_id(lectura_id: str) -> Optional[dict]:
        try:
            oid = ObjectId(lectura_id)
        except Exception:
            return None
        doc = get_lecturas_collection().find_one({"_id": oid})
        return _doc_to_dict(doc) if doc else None
