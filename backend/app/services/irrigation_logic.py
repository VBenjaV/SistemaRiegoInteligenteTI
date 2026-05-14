import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import RiegoAccion
from app.services.database_service import (
    SensorService,
    RiegoService,
    ConfiguracionService,
    ClimaService,
)
from app.services.mqtt_service import get_mqtt_client
from app.services.weather_service import get_weather_service

logger = logging.getLogger(__name__)


class IrrigationLogic:
    """Lógica principal de toma de decisión para riego inteligente"""

    def __init__(self, db: Session, dispositivo_id: str = "sensor1"):
        self.db = db
        self.dispositivo_id = dispositivo_id
        self.mqtt_client = get_mqtt_client()
        self.weather_service = get_weather_service()

    def evaluar_y_actuar(self) -> dict:
        """Evaluar condiciones y actuar en consecuencia
        
        Returns:
            Dict con resultado de la evaluación y acciones tomadas
        """
        resultado = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "humedad_actual": None,
            "umbral": None,
            "lluvia_esperada": None,
            "decision": None,
            "accion_tomada": None,
            "motivo": None,
        }

        try:
            # 1. Obtener datos actuales
            lectura = SensorService.obtener_ultima_lectura(self.db, self.dispositivo_id)
            if not lectura:
                resultado["motivo"] = "No hay lecturas de sensor disponibles"
                logger.warning(f"No hay lecturas para {self.dispositivo_id}")
                return resultado

            config = ConfiguracionService.obtener_configuracion(self.db, self.dispositivo_id)
            resultado["humedad_actual"] = lectura.humedad
            resultado["umbral"] = config.umbral_humedad

            # 2. Verificar si humedad está baja
            if lectura.humedad >= config.umbral_humedad:
                resultado["decision"] = "NO_REGAR"
                resultado["motivo"] = f"Humedad {lectura.humedad}% >= umbral {config.umbral_humedad}%"
                logger.info(resultado["motivo"])
                return resultado

            # 3. Consultar pronóstico meteorológico
            weather_info = self.weather_service.get_complete_weather_info(settings.weather_city)
            resultado["lluvia_esperada"] = weather_info["lluvia_pronostico"]["lluvia_total_mm"]

            if not weather_info["se_debe_regar"]:
                resultado["decision"] = "NO_REGAR"
                resultado["motivo"] = (
                    f"Lluvia esperada {weather_info['lluvia_pronostico']['lluvia_total_mm']}mm "
                    f">= umbral {settings.weather_rain_threshold_mm}mm"
                )
                logger.info(resultado["motivo"])
                return resultado

            # 4. Verificar si ya hay un riego activo
            evento_activo = self._buscar_riego_activo()
            if evento_activo:
                resultado["decision"] = "YA_REGANDO"
                resultado["motivo"] = "Riego ya está activo"
                logger.info(resultado["motivo"])
                return resultado

            # 5. Activar riego
            resultado["decision"] = "REGAR"
            resultado["accion_tomada"] = "ON"
            resultado["motivo"] = (
                f"Humedad {lectura.humedad}% < umbral {config.umbral_humedad}%, "
                f"lluvia esperada {weather_info['lluvia_pronostico']['lluvia_total_mm']}mm"
            )

            # Publicar comando MQTT
            if self.mqtt_client.is_connected():
                exito = self.mqtt_client.publish_command(
                    accion="ON",
                    duracion_segundos=config.intervalo_lectura_min * 60
                )
                if exito:
                    # Registrar evento
                    from app.models import EventoRiegoCreate
                    evento = EventoRiegoCreate(
                        dispositivo_id=self.dispositivo_id,
                        accion=RiegoAccion.ON,
                        duracion_segundos=settings.irrigation_duration_seconds,
                        manual=False
                    )
                    RiegoService.crear_evento(self.db, evento)
                    logger.info(f"Comando de riego publicado: {resultado['motivo']}")
                else:
                    resultado["accion_tomada"] = "ERROR_MQTT"
            else:
                resultado["accion_tomada"] = "ERROR_NO_CONECTADO"
                logger.error("MQTT no está conectado")

        except Exception as e:
            resultado["accion_tomada"] = "ERROR"
            resultado["motivo"] = f"Error en lógica de riego: {str(e)}"
            logger.error(resultado["motivo"], exc_info=True)

        return resultado

    def _buscar_riego_activo(self) -> bool:
        """Buscar si hay un riego activo en los últimos N segundos"""
        evento_activo = RiegoService.obtener_ultimo_evento(self.db, self.dispositivo_id)

        if not evento_activo:
            return False

        # Si el último evento fue apagado
        if evento_activo.accion == "OFF":
            return False

        # Verificar si expiró la duración
        tiempo_transcurrido = (
            datetime.utcnow() - evento_activo.timestamp
        ).total_seconds()

        if tiempo_transcurrido > evento_activo.duracion_segundos:
            # Riego expiró, publicar OFF
            logger.info(f"Riego expirado - duraba {evento_activo.duracion_segundos}s")
            self.mqtt_client.publish_command(accion="OFF", duracion_segundos=0)
            
            from app.models import EventoRiegoCreate
            evento_off = EventoRiegoCreate(
                dispositivo_id=self.dispositivo_id,
                accion=RiegoAccion.OFF,
                duracion_segundos=0,
                manual=False
            )
            RiegoService.crear_evento(self.db, evento_off)
            return False

        return True

    def forzar_riego_on(self, duracion_segundos: Optional[int] = None) -> dict:
        """Activar riego manualmente"""
        if duracion_segundos is None:
            duracion_segundos = settings.irrigation_duration_seconds

        resultado = {
            "exito": False,
            "mensaje": None,
            "duracion_segundos": duracion_segundos,
        }

        try:
            if not self.mqtt_client.is_connected():
                resultado["mensaje"] = "MQTT no conectado"
                return resultado

            exito = self.mqtt_client.publish_command("ON", duracion_segundos)

            if exito:
                from app.models import EventoRiegoCreate
                evento = EventoRiegoCreate(
                    dispositivo_id=self.dispositivo_id,
                    accion=RiegoAccion.ON,
                    duracion_segundos=duracion_segundos,
                    manual=True
                )
                RiegoService.crear_evento(self.db, evento)
                resultado["exito"] = True
                resultado["mensaje"] = "Riego activado manualmente"
                logger.info(resultado["mensaje"])
            else:
                resultado["mensaje"] = "Error publicando comando MQTT"

        except Exception as e:
            resultado["mensaje"] = f"Error: {str(e)}"
            logger.error(resultado["mensaje"], exc_info=True)

        return resultado

    def forzar_riego_off(self) -> dict:
        """Apagar riego manualmente"""
        resultado = {
            "exito": False,
            "mensaje": None,
        }

        try:
            if not self.mqtt_client.is_connected():
                resultado["mensaje"] = "MQTT no conectado"
                return resultado

            exito = self.mqtt_client.publish_command("OFF", 0)

            if exito:
                from app.models import EventoRiegoCreate
                evento = EventoRiegoCreate(
                    dispositivo_id=self.dispositivo_id,
                    accion=RiegoAccion.OFF,
                    duracion_segundos=0,
                    manual=True
                )
                RiegoService.crear_evento(self.db, evento)
                resultado["exito"] = True
                resultado["mensaje"] = "Riego desactivado manualmente"
                logger.info(resultado["mensaje"])
            else:
                resultado["mensaje"] = "Error publicando comando MQTT"

        except Exception as e:
            resultado["mensaje"] = f"Error: {str(e)}"
            logger.error(resultado["mensaje"], exc_info=True)

        return resultado
