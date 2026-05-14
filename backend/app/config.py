from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App Configuration
    debug: bool = True
    api_title: str = "Sistema Riego Inteligente API"
    api_version: str = "1.0.0"
    api_description: str = "API para control automático de riego basado en IoT"

    # Database
    database_url: str = "sqlite:///./riego.db"

    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_topic_subscribe_humidity: str = "jardin/sensor1/humedad"
    mqtt_topic_subscribe_temp: str = "jardin/sensor1/temperatura"
    mqtt_topic_publish_command: str = "jardin/bomba/comando"
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


# Instancia global de configuración
settings = Settings()
