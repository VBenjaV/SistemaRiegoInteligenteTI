"""API endpoints para sensores"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import LecturaSensor, LecturaSensorCreate, LecturaSensorHistorial
from app.services.database_service import SensorService

router = APIRouter(prefix="/api/sensores", tags=["Sensores"])


@router.post(
    "/",
    response_model=LecturaSensor,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva lectura de sensor",
    description="Registra una nueva lectura de humedad del sensor"
)
async def crear_lectura(lectura: LecturaSensorCreate, db: Session = Depends(get_db)):
    """Crear una nueva lectura de sensor"""
    return SensorService.crear_lectura(db, lectura)


@router.get(
    "/actual",
    response_model=LecturaSensor,
    summary="Obtener última lectura",
    description="Retorna la lectura más reciente del sensor"
)
async def obtener_lectura_actual(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener última lectura del sensor"""
    lectura = SensorService.obtener_ultima_lectura(db, dispositivo_id)
    if not lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay lecturas para el dispositivo {dispositivo_id}"
        )
    return lectura


@router.get(
    "/historial",
    response_model=LecturaSensorHistorial,
    summary="Obtener historial de lecturas",
    description="Retorna historial de lecturas con filtros opcionales"
)
async def obtener_historial(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    limit: int = Query(100, ge=1, le=1000, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
    dias: int = Query(None, ge=1, le=365, description="Últimos N días (opcional)"),
    db: Session = Depends(get_db)
):
    """Obtener historial de lecturas de sensores"""
    inicio = None
    fin = None
    
    if dias:
        fin = datetime.utcnow()
        inicio = fin - timedelta(days=dias)
    
    lecturas, total = SensorService.obtener_historial(
        db, dispositivo_id, limit, offset, inicio, fin
    )
    
    return LecturaSensorHistorial(
        total=total,
        lecturas=lecturas,
        inicio=inicio,
        fin=fin
    )


@router.get(
    "/promedio",
    response_model=dict,
    summary="Obtener promedio de humedad",
    description="Calcula el promedio de humedad en el período especificado"
)
async def obtener_promedio(
    dispositivo_id: str = Query("sensor1", description="ID del dispositivo"),
    minutos: int = Query(60, ge=5, le=1440, description="Últimos N minutos"),
    db: Session = Depends(get_db)
):
    """Obtener promedio de humedad"""
    promedio = SensorService.obtener_promedio_humedad(db, dispositivo_id, minutos)
    
    if promedio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay datos para calcular promedio"
        )
    
    return {
        "dispositivo_id": dispositivo_id,
        "promedio_humedad": round(promedio, 2),
        "periodo_minutos": minutos,
        "calculado": datetime.utcnow().isoformat() + "Z"
    }
