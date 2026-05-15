from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class RiegoAccion(str, Enum):
    """Acciones de riego"""
    ON = "ON"
    OFF = "OFF"


# ============================================================================
# Modelos de Sensores
# ============================================================================

class LecturaSensorBase(BaseModel):
    """Base para lecturas de sensores"""
    humedad: float = Field(..., ge=0, le=100, description="Porcentaje de humedad del suelo")
    dispositivo_id: str = Field(default="sensor1", description="ID del sensor")


class LecturaSensorCreate(LecturaSensorBase):
    """Esquema para crear una lectura"""
    temperatura: Optional[float] = Field(None, description="Temperatura en °C")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de lectura (UTC)")


class LecturaSensor(LecturaSensorBase):
    """Lectura de sensor con metadata"""
    id: int
    temperatura: Optional[float] = None
    timestamp: datetime
    creado: datetime

    class Config:
        from_attributes = True


class LecturaSensorHistorial(BaseModel):
    """Respuesta de historial de sensores"""
    total: int
    lecturas: list[LecturaSensor]
    inicio: Optional[datetime] = None
    fin: Optional[datetime] = None


# ============================================================================
# Modelos de Riego
# ============================================================================

class EventoRiegoBase(BaseModel):
    """Base para eventos de riego"""
    accion: RiegoAccion
    duracion_segundos: int = Field(default=300, ge=0)
    manual: bool = Field(default=False, description="¿Fue activado manualmente?")


class EventoRiegoCreate(EventoRiegoBase):
    """Esquema para crear evento"""
    dispositivo_id: str = Field(default="sensor1")
    timestamp: Optional[datetime] = Field(None, description="Timestamp del evento (UTC)")


class EventoRiego(EventoRiegoBase):
    """Evento de riego completo"""
    id: int
    dispositivo_id: str
    timestamp: datetime
    creado: datetime

    class Config:
        from_attributes = True


class EstadoRiego(BaseModel):
    """Estado actual del riego"""
    activo: bool
    duracion_restante_segundos: Optional[int] = None
    ultim_evento: Optional[EventoRiego] = None
    ultima_lectura_humedad: Optional[float] = None


class ControlRiegoManual(BaseModel):
    """Solicitud de control manual"""
    accion: RiegoAccion
    duracion_segundos: int = Field(default=300, ge=60, le=3600)
    dispositivo_id: str = Field(default="sensor1")


class RespuestaControl(BaseModel):
    """Respuesta de control"""
    exito: bool
    mensaje: str
    evento_id: Optional[int] = None


# ============================================================================
# Modelos de Configuración
# ============================================================================

class ConfiguracionBase(BaseModel):
    """Base de configuración"""
    umbral_humedad: int = Field(default=40, ge=0, le=100, description="Umbral de humedad para riego (%)")
    intervalo_lectura_min: int = Field(default=5, ge=1, description="Intervalo de lectura en minutos")
    lluvia_minima_mm: float = Field(default=5.0, ge=0, description="Lluvia mínima para no regar (mm)")
    horas_pronostico: int = Field(default=24, ge=1, le=168, description="Horas de pronóstico a considerar")


class ConfiguracionCreate(ConfiguracionBase):
    """Crear configuración"""
    dispositivo_id: str = Field(default="sensor1")


class Configuracion(ConfiguracionBase):
    """Configuración completa"""
    id: int
    dispositivo_id: str
    actualizado: datetime
    creado: datetime

    class Config:
        from_attributes = True


class ActualizarUmbral(BaseModel):
    """Actualizar umbral de humedad"""
    umbral_humedad: int = Field(..., ge=0, le=100)
    dispositivo_id: str = Field(default="sensor1")


class ActualizarIntervalo(BaseModel):
    """Actualizar intervalo de lectura"""
    intervalo_lectura_min: int = Field(..., ge=1, le=60)
    dispositivo_id: str = Field(default="sensor1")


# ============================================================================
# Modelos de Clima
# ============================================================================

class PronosticoClima(BaseModel):
    """Pronóstico meteorológico"""
    ciudad: str
    fecha: datetime
    lluvia_esperada_mm: float = Field(description="Cantidad de lluvia esperada en mm")
    temperatura_max: Optional[float] = Field(None, description="Temperatura máxima en °C")
    temperatura_min: Optional[float] = Field(None, description="Temperatura mínima en °C")
    humedad_relativa: Optional[int] = Field(None, description="Humedad relativa (%)")
    descripcion: Optional[str] = Field(None, description="Descripción del clima")
    actualizado: datetime

    class Config:
        from_attributes = True


class InformacionClima(BaseModel):
    """Información actual de clima"""
    ciudad: str
    temperatura: float
    humedad_relativa: int
    descripcion: str
    lluvia_hoy_mm: float
    pronostico_lluvia_24h_mm: float
    actualizado: datetime


# ============================================================================
# Modelos de Respuesta de API
# ============================================================================

class RespuestaExito(BaseModel):
    """Respuesta genérica de éxito"""
    exito: bool = True
    mensaje: str
    datos: Optional[dict] = None


class RespuestaError(BaseModel):
    """Respuesta de error"""
    exito: bool = False
    error: str
    detalles: Optional[str] = None


class DashboardActual(BaseModel):
    """Dashboard con información actual"""
    humedad_actual: Optional[float] = None
    temperatura_actual: Optional[float] = None
    riego_activo: bool = False
    duracion_riego_restante: Optional[int] = None
    clima_ciudad: str
    clima_temperatura: Optional[float] = None
    clima_lluvia_24h: Optional[float] = None
    umbral_humedad: int
    ultimo_evento_riego: Optional[EventoRiego] = None
    actualizado: datetime
