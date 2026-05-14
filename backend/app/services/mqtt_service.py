import logging
import json
from datetime import datetime
from typing import Callable, Optional
import paho.mqtt.client as mqtt
from threading import Lock

from app.config import settings

logger = logging.getLogger(__name__)


class MQTTClient:
    """Cliente MQTT para comunicación con sensores y actuadores"""

    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=settings.mqtt_client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        self.connected = False
        self.lock = Lock()
        
        # Callbacks personalizados
        self._on_message_callback: Optional[Callable] = None
        
        # Configurar credenciales si existen
        if settings.mqtt_username and settings.mqtt_password:
            self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

    def _on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"Conectado a MQTT broker: {settings.mqtt_broker_host}:{settings.mqtt_broker_port}")
            
            # Suscribirse a temas
            self.client.subscribe(settings.mqtt_topic_subscribe_humidity)
            self.client.subscribe(settings.mqtt_topic_subscribe_temp)
            logger.info(f"Suscrito a temas: {settings.mqtt_topic_subscribe_humidity}, {settings.mqtt_topic_subscribe_temp}")
        else:
            logger.error(f"Error de conexión MQTT - código: {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """Callback cuando se desconecta del broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Desconexión inesperada del MQTT broker - código: {rc}")
        else:
            logger.info("Desconectado del MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback cuando se recibe un mensaje"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.debug(f"Mensaje recibido en {msg.topic}: {payload}")
            
            # Llamar al callback personalizado si existe
            if self._on_message_callback:
                self._on_message_callback(msg.topic, payload)
        except Exception as e:
            logger.error(f"Error procesando mensaje MQTT: {e}")

    def _on_publish(self, client, userdata, mid):
        """Callback cuando se publica un mensaje"""
        logger.debug(f"Mensaje publicado - ID: {mid}")

    def connect(self):
        """Conectar al broker MQTT"""
        try:
            logger.info(f"Intentando conectar a {settings.mqtt_broker_host}:{settings.mqtt_broker_port}")
            self.client.connect(
                settings.mqtt_broker_host,
                settings.mqtt_broker_port,
                keepalive=settings.mqtt_keepalive
            )
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Error conectando a MQTT: {e}")
            raise

    def disconnect(self):
        """Desconectar del broker MQTT"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Desconectado de MQTT broker")
        except Exception as e:
            logger.error(f"Error desconectando de MQTT: {e}")

    def publish_command(self, accion: str, duracion_segundos: int = 0) -> bool:
        """Publicar comando de riego
        
        Args:
            accion: "ON" o "OFF"
            duracion_segundos: duración en segundos (para ON)
            
        Returns:
            True si se publicó exitosamente
        """
        try:
            payload = {
                "accion": accion,
                "duracion_segundos": duracion_segundos,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            result = self.client.publish(
                settings.mqtt_topic_publish_command,
                json.dumps(payload),
                qos=1
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Comando de riego publicado: {payload}")
                return True
            else:
                logger.error(f"Error publicando comando: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error al publicar comando MQTT: {e}")
            return False

    def set_message_callback(self, callback: Callable):
        """Establecer callback personalizado para mensajes"""
        self._on_message_callback = callback

    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self.connected


# Instancia global
mqtt_client: Optional[MQTTClient] = None


def get_mqtt_client() -> MQTTClient:
    """Obtener instancia global del cliente MQTT"""
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = MQTTClient()
    return mqtt_client


async def init_mqtt():
    """Inicializar conexión MQTT"""
    client = get_mqtt_client()
    client.connect()


async def close_mqtt():
    """Cerrar conexión MQTT"""
    client = get_mqtt_client()
    client.disconnect()
