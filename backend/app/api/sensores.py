"""API endpoints para sensores (MongoDB)"""
from fastapi import APIRouter, Query, HTTPException, status
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.models import LecturaSensor, LecturaSensorCreate, LecturaSensorHistorial
from app.services.mongo_sensor_service import MongoSensorService

router = APIRouter(prefix="/api/sensores", tags=["Sensores"])


@router.post(
    "/",
    response_model=LecturaSensor,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva lectura de sensor",
    description="Registra una nueva lectura de humedad del sensor en MongoDB",
)
async def crear_lectura(lectura: LecturaSensorCreate):
    doc = MongoSensorService.crear_lectura(lectura)
    return LecturaSensor(**doc)


@router.get(
    "/actual",
    response_model=LecturaSensor,
    summary="Obtener última lectura",
    description="Retorna la lectura más reciente del sensor",
)
async def obtener_lectura_actual(
    dispositivo_id: str = Query(
        default=None,
        description="ID del dispositivo",
    ),
):
    device = dispositivo_id or settings.dispositivo_default_id
    lectura = MongoSensorService.obtener_ultima_lectura(device)
    if not lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay lecturas para el dispositivo {device}",
        )
    return LecturaSensor(**lectura)


@router.get(
    "/historial",
    response_model=LecturaSensorHistorial,
    summary="Obtener historial de lecturas",
    description="Retorna historial de lecturas con filtros opcionales",
)
async def obtener_historial(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    limit: int = Query(100, ge=1, le=1000, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
    dias: int = Query(None, ge=1, le=365, description="Últimos N días (opcional)"),
):
    device = dispositivo_id or settings.dispositivo_default_id
    inicio = None
    fin = None

    if dias:
        fin = datetime.now(timezone.utc)
        inicio = fin - timedelta(days=dias)

    lecturas, total = MongoSensorService.obtener_historial(
        device, limit, offset, inicio, fin
    )

    return LecturaSensorHistorial(
        total=total,
        lecturas=[LecturaSensor(**l) for l in lecturas],
        inicio=inicio,
        fin=fin,
    )


@router.get(
    "/promedio",
    response_model=dict,
    summary="Obtener promedio de humedad",
    description="Calcula el promedio de humedad en el período especificado",
)
async def obtener_promedio(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    minutos: int = Query(60, ge=5, le=1440, description="Últimos N minutos"),
):
    device = dispositivo_id or settings.dispositivo_default_id
    promedio = MongoSensorService.obtener_promedio_humedad(device, minutos)

    if promedio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos para calcular promedio",
        )

    return {
        "dispositivo_id": device,
        "promedio_humedad": round(promedio, 2),
        "periodo_minutos": minutos,
        "calculado": datetime.now(timezone.utc).isoformat(),
    }
