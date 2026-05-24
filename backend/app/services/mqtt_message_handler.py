import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.config import settings
from app.models import LecturaSensorCreate
from app.services.mongo_sensor_service import MongoSensorService

logger = logging.getLogger(__name__)


def _parse_timestamp(value: Any) -> Optional[datetime]:
    """Interpretar timestamp del payload o usar hora del servidor."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        n = float(value)
        # Valores pequeños (ej. 211050) = uptime del ESP en ms/seg, no Unix
        if n < 1_000_000_000:
            return datetime.now(timezone.utc)
        if n >= 1_000_000_000_000:
            return datetime.fromtimestamp(n / 1000, tz=timezone.utc)
        return datetime.fromtimestamp(n, tz=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            return None
    return None


def _get_humedad(data: dict[str, Any]) -> Optional[float]:
    """Humedad del suelo: admite claves con espacios (ej. 'humedad suelo')."""
    for key, val in data.items():
        k = key.lower().replace("_", " ").strip()
        if k in ("humedad", "humedad suelo", "humidity", "soil moisture", "moisture"):
            return float(val)
    return None


def _extract_reading(payload: str) -> Optional[LecturaSensorCreate]:
    """Interpretar payload JSON o numérico del ESP8266."""
    payload = payload.strip()
    data: dict[str, Any] = {}

    try:
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            data = parsed
        elif isinstance(parsed, (int, float)):
            data = {"humedad": float(parsed)}
        else:
            return None
    except json.JSONDecodeError:
        try:
            data = {"humedad": float(payload)}
        except ValueError:
            logger.warning("Payload MQTT no reconocido: %s", payload[:200])
            return None

    humedad = _get_humedad(data)
    if humedad is None:
        logger.warning("Payload sin campo de humedad: %s", data)
        return None

    temperatura = (
        data.get("temperatura")
        or data.get("temperature")
        or data.get("temp")
    )

    lectura = LecturaSensorCreate(
        humedad=humedad,
        temperatura=float(temperatura) if temperatura is not None else None,
        dispositivo_id=str(
            data.get("dispositivo_id")
            or data.get("device_id")
            or data.get("id")
            or settings.dispositivo_default_id
        ),
        timestamp=_parse_timestamp(
            data.get("timestamp") or data.get("ts") or data.get("time")
        ),
    )
    logger.info(
        "Lectura ESP: humedad=%.1f%% temp=%s",
        lectura.humedad,
        lectura.temperatura,
    )
    return lectura


def _is_sensor_publish_topic(topic: str) -> bool:
    """Coincidencia exacta del topic (MQTT distingue mayúsculas/minúsculas)."""
    return topic.strip() == settings.mqtt_topic_subscribe.strip()


def process_mqtt_message(topic: str, payload: str) -> None:
    """Guardar en MongoDB mensajes del topic de publicación del ESP."""
    if not _is_sensor_publish_topic(topic):
        logger.warning("Topic ignorado: %s (esperado tipo */pub del ESP)", topic)
        return

    logger.info("MQTT recibido [%s]: %s", topic, payload[:300])

    lectura = _extract_reading(payload)
    if not lectura:
        return

    try:
        MongoSensorService.crear_lectura(
            lectura,
            topic=topic,
            payload_raw=payload,
        )
    except Exception as e:
        logger.error("Error guardando lectura en MongoDB: %s", e, exc_info=True)
