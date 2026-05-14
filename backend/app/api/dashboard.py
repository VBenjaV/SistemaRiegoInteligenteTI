"""API endpoints para dashboard"""
from fastapi import APIRouter, Depends, Query
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.config import settings
from app.models import DashboardActual
from app.services.database_service import (
    SensorService,
    RiegoService,
    ConfiguracionService,
)
from app.services.weather_service import get_weather_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/actual",
    response_model=DashboardActual,
    summary="Dashboard en tiempo real",
    description="Retorna toda la información actual para el dashboard"
)
async def obtener_dashboard(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener datos para dashboard"""
    
    # Obtener sensor actual
    ultima_lectura = SensorService.obtener_ultima_lectura(db, dispositivo_id)
    
    # Obtener configuración
    config = ConfiguracionService.obtener_configuracion(db, dispositivo_id)
    
    # Obtener estado de riego
    ultimo_evento = RiegoService.obtener_ultimo_evento(db, dispositivo_id)
    
    riego_activo = False
    duracion_restante = None
    if ultimo_evento and ultimo_evento.accion == "ON":
        tiempo_transcurrido = (
            datetime.utcnow() - ultimo_evento.timestamp
        ).total_seconds()
        
        if tiempo_transcurrido < ultimo_evento.duracion_segundos:
            riego_activo = True
            duracion_restante = int(
                ultimo_evento.duracion_segundos - tiempo_transcurrido
            )
    
    # Obtener clima
    weather_service = get_weather_service()
    clima_info = {
        "temperatura": None,
        "lluvia_24h": None
    }
    
    if weather_service.api_key:
        try:
            weather_data = weather_service.get_complete_weather_info(settings.weather_city)
            clima_info["temperatura"] = weather_data["clima_actual"].get("temperatura")
            clima_info["lluvia_24h"] = weather_data["lluvia_pronostico"].get("lluvia_total_mm")
        except:
            pass
    
    return DashboardActual(
        humedad_actual=ultima_lectura.humedad if ultima_lectura else None,
        temperatura_actual=ultima_lectura.temperatura if ultima_lectura else None,
        riego_activo=riego_activo,
        duracion_riego_restante=duracion_restante,
        clima_ciudad=settings.weather_city,
        clima_temperatura=clima_info["temperatura"],
        clima_lluvia_24h=clima_info["lluvia_24h"],
        umbral_humedad=config.umbral_humedad,
        ultimo_evento_riego=ultimo_evento,
        actualizado=datetime.utcnow()
    )


@router.get(
    "/resumen",
    response_model=dict,
    summary="Resumen del sistema",
    description="Retorna un resumen rápido del estado del sistema"
)
async def obtener_resumen(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener resumen rápido"""
    
    ultima_lectura = SensorService.obtener_ultima_lectura(db, dispositivo_id)
    config = ConfiguracionService.obtener_configuracion(db, dispositivo_id)
    ultimo_evento = RiegoService.obtener_ultimo_evento(db, dispositivo_id)
    tiempo_riego_hoy = RiegoService.obtener_tiempo_riego_total_hoy(db, dispositivo_id)
    promedio = SensorService.obtener_promedio_humedad(db, dispositivo_id, minutos=60)
    
    return {
        "dispositivo_id": dispositivo_id,
        "humedad": {
            "actual": ultima_lectura.humedad if ultima_lectura else None,
            "promedio_1h": round(promedio, 2) if promedio else None,
            "umbral": config.umbral_humedad
        },
        "riego": {
            "activo": ultimo_evento.accion == "ON" if ultimo_evento else False,
            "ultimo_evento": ultimo_evento.accion if ultimo_evento else None,
            "tiempo_total_hoy_min": round(tiempo_riego_hoy / 60, 2)
        },
        "actualizado": datetime.utcnow().isoformat() + "Z"
    }
