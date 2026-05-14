"""API endpoints para configuración"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Configuracion, ActualizarUmbral, ActualizarIntervalo
from app.services.database_service import ConfiguracionService

router = APIRouter(prefix="/api/config", tags=["Configuración"])


@router.get(
    "/",
    response_model=Configuracion,
    summary="Obtener configuración",
    description="Retorna configuración actual del sistema"
)
async def obtener_configuracion(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener configuración del dispositivo"""
    return ConfiguracionService.obtener_configuracion(db, dispositivo_id)


@router.put(
    "/umbral",
    response_model=Configuracion,
    summary="Actualizar umbral de humedad",
    description="Modifica el umbral de humedad para activar riego"
)
async def actualizar_umbral(
    actualizacion: ActualizarUmbral,
    db: Session = Depends(get_db)
):
    """Actualizar umbral de humedad"""
    config = ConfiguracionService.actualizar_umbral(
        db, actualizacion.dispositivo_id, actualizacion.umbral_humedad
    )
    return config


@router.put(
    "/intervalo",
    response_model=Configuracion,
    summary="Actualizar intervalo de lectura",
    description="Modifica cada cuántos minutos se lee el sensor"
)
async def actualizar_intervalo(
    actualizacion: ActualizarIntervalo,
    db: Session = Depends(get_db)
):
    """Actualizar intervalo de lectura"""
    config = ConfiguracionService.actualizar_intervalo(
        db, actualizacion.dispositivo_id, actualizacion.intervalo_lectura_min
    )
    return config


@router.get(
    "/umbral",
    response_model=dict,
    summary="Obtener umbral actual",
    description="Retorna el umbral de humedad configurado"
)
async def obtener_umbral(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener umbral de humedad"""
    config = ConfiguracionService.obtener_configuracion(db, dispositivo_id)
    return {
        "dispositivo_id": dispositivo_id,
        "umbral_humedad_percent": config.umbral_humedad,
        "descripcion": "Si la humedad cae por debajo de este valor, se activa el riego"
    }
