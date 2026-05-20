"""API endpoints para riego"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import (
    EventoRiego,
    EventoRiegoCreate,
    EstadoRiego,
    ControlRiegoManual,
    RespuestaControl,
    RiegoAccion,
)
from app.config import settings
from app.services.database_service import (
    RiegoService,
    ConfiguracionService,
)
from app.services.mongo_sensor_service import MongoSensorService
from app.services.irrigation_logic import IrrigationLogic

router = APIRouter(prefix="/api/riego", tags=["Riego"])


@router.get(
    "/estado",
    response_model=EstadoRiego,
    summary="Obtener estado actual del riego",
    description="Retorna si el riego está activo y cuánto tiempo falta"
)
async def obtener_estado(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener estado actual del riego"""
    device = dispositivo_id or settings.dispositivo_default_id
    ultimo_evento = RiegoService.obtener_ultimo_evento(db, device)
    ultima_lectura = MongoSensorService.obtener_ultima_lectura(device)
    
    activo = False
    duracion_restante = None
    
    if ultimo_evento and ultimo_evento.accion == "ON":
        tiempo_transcurrido = (
            datetime.utcnow() - ultimo_evento.timestamp
        ).total_seconds()
        
        if tiempo_transcurrido < ultimo_evento.duracion_segundos:
            activo = True
            duracion_restante = int(
                ultimo_evento.duracion_segundos - tiempo_transcurrido
            )
    
    return EstadoRiego(
        activo=activo,
        duracion_restante_segundos=duracion_restante,
        ultim_evento=ultimo_evento,
        ultima_lectura_humedad=ultima_lectura["humedad"] if ultima_lectura else None
    )


@router.get(
    "/historial",
    response_model=dict,
    summary="Obtener historial de riego",
    description="Retorna log de ciclos de riego"
)
async def obtener_historial(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    limit: int = Query(50, ge=1, le=500, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
    dias: int = Query(None, ge=1, le=365, description="Últimos N días (opcional)"),
    db: Session = Depends(get_db)
):
    """Obtener historial de eventos de riego"""
    device = dispositivo_id or settings.dispositivo_default_id
    inicio = None
    fin = None

    if dias:
        fin = datetime.utcnow()
        inicio = fin - timedelta(days=dias)

    eventos, total = RiegoService.obtener_historial(
        db, device, limit, offset, inicio, fin
    )

    return {
        "total": total,
        "eventos": eventos,
        "dispositivo_id": device,
        "periodo": {
            "inicio": inicio,
            "fin": fin
        }
    }


@router.post(
    "/evaluar",
    response_model=dict,
    summary="Evaluar y ejecutar lógica de riego",
    description="Ejecuta el algoritmo de toma de decisión para riego inteligente"
)
async def evaluar_riego(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Evaluar y actuar en lógica de riego"""
    logic = IrrigationLogic(db, dispositivo_id)
    resultado = logic.evaluar_y_actuar()
    return resultado


@router.post(
    "/forzar-on",
    response_model=RespuestaControl,
    summary="Activar riego manualmente",
    description="Fuerza el encendido del sistema de riego"
)
async def forzar_riego_on(
    comando: ControlRiegoManual,
    db: Session = Depends(get_db)
):
    """Forzar activación de riego"""
    logic = IrrigationLogic(db, comando.dispositivo_id)
    resultado = logic.forzar_riego_on(comando.duracion_segundos)
    
    return RespuestaControl(
        exito=resultado["exito"],
        mensaje=resultado["mensaje"],
        evento_id=None
    )


@router.post(
    "/forzar-off",
    response_model=RespuestaControl,
    summary="Desactivar riego manualmente",
    description="Apaga el sistema de riego"
)
async def forzar_riego_off(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Forzar desactivación de riego"""
    logic = IrrigationLogic(db, dispositivo_id)
    resultado = logic.forzar_riego_off()
    
    return RespuestaControl(
        exito=resultado["exito"],
        mensaje=resultado["mensaje"],
        evento_id=None
    )


@router.get(
    "/tiempo-total-hoy",
    response_model=dict,
    summary="Tiempo total de riego hoy",
    description="Retorna cantidad total de segundos que el riego estuvo activo"
)
async def obtener_tiempo_total_hoy(
    dispositivo_id: str = Query(default=None, description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """Obtener tiempo total de riego hoy"""
    device = dispositivo_id or settings.dispositivo_default_id
    segundos = RiegoService.obtener_tiempo_riego_total_hoy(db, device)
    horas = segundos / 3600
    minutos = (segundos % 3600) / 60
    
    return {
        "dispositivo_id": device,
        "fecha": datetime.utcnow().date().isoformat(),
        "tiempo_total_segundos": segundos,
        "tiempo_total_horas": round(horas, 2),
        "tiempo_total_minutos": round(minutos, 2),
    }
