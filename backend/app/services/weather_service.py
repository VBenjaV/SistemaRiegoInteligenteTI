import logging
from datetime import datetime, timedelta
import requests
from typing import Optional
from app.config import settings
from app.models import PronosticoClima

logger = logging.getLogger(__name__)


class WeatherService:
    """Servicio para obtener datos meteorológicos de OpenWeatherMap"""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.weather_api_key
        if not self.api_key:
            logger.warning("No se configuró clave de API para OpenWeatherMap")

    def get_current_weather(self, city: str) -> Optional[dict]:
        """Obtener clima actual de una ciudad
        
        Args:
            city: Nombre de la ciudad
            
        Returns:
            Diccionario con datos del clima actual o None si hay error
        """
        if not self.api_key:
            logger.warning("API key no configurada - no se puede obtener clima")
            return None

        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "es"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Clima actual obtenido para {city}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo clima de {city}: {e}")
            return None

    def get_forecast(self, city: str, hours: int = 24) -> Optional[dict]:
        """Obtener pronóstico de 5 días (datos cada 3 horas)
        
        Args:
            city: Nombre de la ciudad
            hours: Horas en el futuro a considerar
            
        Returns:
            Diccionario con datos del pronóstico o None si hay error
        """
        if not self.api_key:
            logger.warning("API key no configurada - no se puede obtener pronóstico")
            return None

        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "es"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Filtrar pronóstico a las horas solicitadas
            filtered_data = self._filter_forecast_by_hours(data, hours)
            logger.info(f"Pronóstico obtenido para {city} ({hours} horas)")
            return filtered_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo pronóstico para {city}: {e}")
            return None

    def _filter_forecast_by_hours(self, forecast_data: dict, hours: int) -> dict:
        """Filtrar pronóstico a un número de horas específico
        
        Args:
            forecast_data: Datos completos del pronóstico
            hours: Número de horas a considerar
            
        Returns:
            Forecast filtrado
        """
        now = datetime.utcnow()
        cutoff_time = now + timedelta(hours=hours)
        
        filtered_list = [
            item for item in forecast_data.get("list", [])
            if datetime.fromtimestamp(item["dt"]) <= cutoff_time
        ]
        
        forecast_data["list"] = filtered_list
        return forecast_data

    def extract_rain_info(self, forecast_data: Optional[dict]) -> dict:
        """Extraer información de lluvia del pronóstico
        
        Returns:
            Dict con: {
                'lluvia_total_mm': float,
                'hay_lluvia': bool,
                'horas_con_lluvia': int,
                'intensidad_max': float
            }
        """
        result = {
            "lluvia_total_mm": 0.0,
            "hay_lluvia": False,
            "horas_con_lluvia": 0,
            "intensidad_max": 0.0,
            "pronostico_items": 0
        }

        if not forecast_data or "list" not in forecast_data:
            return result

        for item in forecast_data["list"]:
            # Lluvia (rain)
            rain_mm = item.get("rain", {}).get("3h", 0)  # Datos cada 3 horas
            result["lluvia_total_mm"] += rain_mm
            
            if rain_mm > 0:
                result["hay_lluvia"] = True
                result["horas_con_lluvia"] += 3  # Cada item es de 3 horas
                result["intensidad_max"] = max(result["intensidad_max"], rain_mm)
            
            result["pronostico_items"] += 1

        return result

    def extract_weather_summary(self, weather_data: Optional[dict]) -> dict:
        """Extraer información resumida del clima actual
        
        Returns:
            Dict con información del clima
        """
        if not weather_data:
            return {
                "temperatura": None,
                "humedad": None,
                "descripcion": "No disponible",
                "ciudad": None
            }

        try:
            main = weather_data.get("main", {})
            weather = weather_data.get("weather", [{}])[0]
            
            return {
                "temperatura": main.get("temp"),
                "humedad": main.get("humidity"),
                "descripcion": weather.get("description", "").capitalize(),
                "ciudad": weather_data.get("name"),
                "pais": weather_data.get("sys", {}).get("country"),
                "velocidad_viento": main.get("wind", {}).get("speed")
            }
        except Exception as e:
            logger.error(f"Error extrayendo información del clima: {e}")
            return {
                "temperatura": None,
                "humedad": None,
                "descripcion": "Error",
                "ciudad": None
            }

    def should_irrigate_based_on_weather(self, forecast_data: Optional[dict]) -> bool:
        """Determinar si se debe regar basado en el pronóstico
        
        Args:
            forecast_data: Datos del pronóstico
            
        Returns:
            True si se debe regar (lluvia mínima), False si no se debe
        """
        rain_info = self.extract_rain_info(forecast_data)
        
        # No regar si se espera lluvia significativa
        if rain_info["lluvia_total_mm"] >= settings.weather_rain_threshold_mm:
            logger.info(
                f"No se recomienda riego: lluvia esperada {rain_info['lluvia_total_mm']}mm "
                f">= umbral {settings.weather_rain_threshold_mm}mm"
            )
            return False
        
        logger.info(
            f"Riego recomendado: lluvia esperada {rain_info['lluvia_total_mm']}mm "
            f"< umbral {settings.weather_rain_threshold_mm}mm"
        )
        return True

    def get_complete_weather_info(self, city: str) -> dict:
        """Obtener información completa de clima y pronóstico
        
        Args:
            city: Nombre de la ciudad
            
        Returns:
            Dict combinado con clima actual y pronóstico
        """
        current = self.get_current_weather(city)
        forecast = self.get_forecast(city, settings.weather_forecast_hours)
        
        current_summary = self.extract_weather_summary(current)
        rain_info = self.extract_rain_info(forecast)
        
        return {
            "clima_actual": current_summary,
            "lluvia_pronostico": rain_info,
            "se_debe_regar": self.should_irrigate_based_on_weather(forecast),
            "actualizado": datetime.utcnow().isoformat() + "Z"
        }


# Instancia global
weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Obtener instancia global del servicio de clima"""
    global weather_service
    if weather_service is None:
        weather_service = WeatherService()
    return weather_service
