import logging
from typing import Optional

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import settings

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongodb_url)
        logger.info("Cliente MongoDB conectado a %s", settings.mongodb_url)
    return _client


def get_mongo_db() -> Database:
    global _db
    if _db is None:
        _db = get_mongo_client()[settings.mongodb_database]
    return _db


def get_lecturas_collection() -> Collection:
    return get_mongo_db()[settings.mongodb_collection_lecturas]


def init_mongo():
    """Crear índices para consultas de lecturas."""
    collection = get_lecturas_collection()
    collection.create_index(
        [("dispositivo_id", ASCENDING), ("timestamp", DESCENDING)],
        name="ix_dispositivo_timestamp",
    )
    logger.info(
        "MongoDB listo: db=%s colección=%s",
        settings.mongodb_database,
        settings.mongodb_collection_lecturas,
    )


def close_mongo():
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("Conexión MongoDB cerrada")
