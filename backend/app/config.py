from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# Rutas del repositorio (backend/app -> repo root)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_IOT_CORE_DIR = _REPO_ROOT / "IotCore"
_CERT_PREFIX = "4bb52c4252bfb1b205ea09eb59a655000d689f05c3b72aa689f775caa548496e"


class Settings(BaseSettings):
    # App Configuration
    debug: bool = True
    api_title: str = "Sistema Riego Inteligente API"
    api_version: str = "1.0.0"
    api_description: str = "API para control automático de riego basado en IoT"

    # Database (Supabase/PostgreSQL para config, riego, clima)
    supabase_db_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # MongoDB (lecturas de sensores desde IoT Core)
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "riego_inteligente"
    mongodb_collection_lecturas: str = "lecturas_sensores"
    dispositivo_default_id: str = "esp8266"

    # AWS IoT Core (MQTT sobre TLS)
    aws_iot_endpoint: str = ""
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 8883
    mqtt_use_tls: bool = True
    mqtt_ca_path: str = str(_IOT_CORE_DIR / "AmazonRootCA1.pem")
    mqtt_cert_path: str = str(_IOT_CORE_DIR / f"{_CERT_PREFIX}-certificate.pem.crt")
    mqtt_key_path: str = str(_IOT_CORE_DIR / f"{_CERT_PREFIX}-private.pem.key")
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_topic_subscribe: str = "esp8266/pub"
    mqtt_topic_publish: str = "esp8226/sub"
    mqtt_client_id: str = "riego-backend-1"
    mqtt_keepalive: int = 60

    # Weather API
    weather_api_key: Optional[str] = None
    weather_city: str = "Mexico City"
    weather_update_interval_hours: int = 1
    weather_rain_threshold_mm: float = 5.0
    weather_forecast_hours: int = 24

    # Irrigation Logic
    humidity_threshold_percent: int = 40
    irrigation_duration_seconds: int = 300
    sensor_read_interval_minutes: int = 5

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def sqlalchemy_database_url(self) -> str:
        # Opcional: si no está configurada, retorna None
        return self.supabase_db_url or None

    @property
    def mqtt_host(self) -> str:
        """Host del broker: endpoint AWS IoT o host local."""
        if self.aws_iot_endpoint:
            return self.aws_iot_endpoint.strip()
        return self.mqtt_broker_host


# Instancia global de configuración
settings = Settings()
