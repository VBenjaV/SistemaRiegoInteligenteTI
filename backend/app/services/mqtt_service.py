import logging
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from app.config import settings
from app.services.mqtt_message_handler import process_mqtt_message

logger = logging.getLogger(__name__)


class MQTTClient:
    """Cliente MQTT para AWS IoT Core (TLS) o broker local."""

    def __init__(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            client_id=settings.mqtt_client_id,
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish

        self.connected = False
        self._on_message_callback: Optional[Callable] = None

        if settings.mqtt_use_tls:
            self._configure_tls()
        elif settings.mqtt_username and settings.mqtt_password:
            self.client.username_pw_set(
                settings.mqtt_username,
                settings.mqtt_password,
            )

    def _configure_tls(self):
        """Configurar certificados para AWS IoT Core."""
        for path, label in (
            (settings.mqtt_ca_path, "CA"),
            (settings.mqtt_cert_path, "certificado"),
            (settings.mqtt_key_path, "clave privada"),
        ):
            if not Path(path).is_file():
                raise FileNotFoundError(
                    f"Archivo {label} MQTT no encontrado: {path}"
                )

        self.client.tls_set(
            ca_certs=settings.mqtt_ca_path,
            certfile=settings.mqtt_cert_path,
            keyfile=settings.mqtt_key_path,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
            ciphers=None,
        )
        self.client.tls_insecure_set(False)
        logger.info("TLS configurado con certificados de %s", Path(settings.mqtt_ca_path).parent)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            host = settings.mqtt_host
            logger.info(
                "Conectado a MQTT: %s:%s (TLS=%s)",
                host,
                settings.mqtt_broker_port,
                settings.mqtt_use_tls,
            )
            client.subscribe(settings.mqtt_topic_subscribe, qos=1)
            logger.info(
                "Suscrito a: %s | Publica comandos en: %s",
                settings.mqtt_topic_subscribe,
                settings.mqtt_topic_publish,
            )
        else:
            logger.error("Error de conexión MQTT - código: %s", rc)
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logger.warning("Desconexión inesperada MQTT - código: %s", rc)
        else:
            logger.info("Desconectado del broker MQTT")

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")
            logger.info("MQTT raw [%s]: %s", msg.topic, payload[:300])

            process_mqtt_message(msg.topic, payload)

            if self._on_message_callback:
                self._on_message_callback(msg.topic, payload)
        except Exception as e:
            logger.error("Error procesando mensaje MQTT: %s", e)

    def _on_publish(self, client, userdata, mid):
        logger.debug("Mensaje publicado - ID: %s", mid)

    def connect(self):
        try:
            host = settings.mqtt_host
            if not host:
                raise ValueError(
                    "Configure AWS_IOT_ENDPOINT o MQTT_BROKER_HOST en .env"
                )

            logger.info(
                "Conectando a %s:%s...",
                host,
                settings.mqtt_broker_port,
            )
            self.client.connect(
                host,
                settings.mqtt_broker_port,
                keepalive=settings.mqtt_keepalive,
            )
            self.client.loop_start()
        except Exception as e:
            logger.error("Error conectando a MQTT: %s", e)
            raise

    def disconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Desconectado de MQTT")
        except Exception as e:
            logger.error("Error desconectando MQTT: %s", e)

    def publish_command(self, accion: str, duracion_segundos: int = 0) -> bool:
        """Publicar comando de riego en ESP8266/sub."""
        try:
            payload = {
                "accion": accion,
                "duracion_segundos": duracion_segundos,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            result = self.client.publish(
                settings.mqtt_topic_publish,
                json.dumps(payload),
                qos=1,
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info("Comando publicado en %s: %s", settings.mqtt_topic_publish, payload)
                return True
            logger.error("Error publicando comando: %s", result.rc)
            return False
        except Exception as e:
            logger.error("Error al publicar comando MQTT: %s", e)
            return False

    def set_message_callback(self, callback: Callable):
        self._on_message_callback = callback

    def is_connected(self) -> bool:
        return self.connected


mqtt_client: Optional[MQTTClient] = None


def get_mqtt_client() -> MQTTClient:
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = MQTTClient()
    return mqtt_client


async def init_mqtt():
    client = get_mqtt_client()
    client.connect()


async def close_mqtt():
    client = get_mqtt_client()
    client.disconnect()
