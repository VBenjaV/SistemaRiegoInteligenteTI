import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import (
    LecturaSensorDB,
    EventoRiegoDB,
    ConfiguracionDB,
    PronosticoClimaDB,
)
from app.models import (
    LecturaSensorCreate,
    EventoRiegoCreate,
    ConfiguracionCreate,
)

logger = logging.getLogger(__name__)


class SensorService:
    """Servicio para gestionar lecturas de sensores"""

    @staticmethod
    def crear_lectura(db: Session, lectura: LecturaSensorCreate) -> LecturaSensorDB:
        """Crear nueva lectura de sensor"""
        db_lectura = LecturaSensorDB(
            dispositivo_id=lectura.dispositivo_id,
            humedad=lectura.humedad,
            temperatura=lectura.temperatura,
            timestamp=lectura.timestamp or datetime.now(timezone.utc)
        )
        db.add(db_lectura)
        db.commit()
        db.refresh(db_lectura)
        logger.info(f"Lectura guardada: humedad={lectura.humedad}%, dispositivo={lectura.dispositivo_id}")
        return db_lectura

    @staticmethod
    def obtener_ultima_lectura(db: Session, dispositivo_id: str = "sensor1") -> Optional[LecturaSensorDB]:
        """Obtener última lectura de un dispositivo"""
        return db.query(LecturaSensorDB).filter(
            LecturaSensorDB.dispositivo_id == dispositivo_id
        ).order_by(LecturaSensorDB.timestamp.desc()).first()

    @staticmethod
    def obtener_historial(
        db: Session,
        dispositivo_id: str = "sensor1",
        limit: int = 100,
        offset: int = 0,
        inicio: Optional[datetime] = None,
        fin: Optional[datetime] = None,
    ) -> tuple[list[LecturaSensorDB], int]:
        """Obtener historial de lecturas con filtros"""
        query = db.query(LecturaSensorDB).filter(
            LecturaSensorDB.dispositivo_id == dispositivo_id
        )
        
        if inicio:
            query = query.filter(LecturaSensorDB.timestamp >= inicio)
        if fin:
            query = query.filter(LecturaSensorDB.timestamp <= fin)
        
        total = query.count()
        lecturas = query.order_by(
            LecturaSensorDB.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        return lecturas, total

    @staticmethod
    def obtener_promedio_humedad(
        db: Session,
        dispositivo_id: str = "sensor1",
        minutos: int = 60
    ) -> Optional[float]:
        """Obtener promedio de humedad en los últimos N minutos"""
        from datetime import timedelta
        
        tiempo_limite = datetime.now(timezone.utc) - timedelta(minutes=minutos)
        from sqlalchemy import func
        
        resultado = db.query(func.avg(LecturaSensorDB.humedad)).filter(
            LecturaSensorDB.dispositivo_id == dispositivo_id,
            LecturaSensorDB.timestamp >= tiempo_limite
        ).scalar()
        
        return resultado


class RiegoService:
    """Servicio para gestionar eventos de riego"""

    @staticmethod
    def crear_evento(db: Session, evento: EventoRiegoCreate) -> EventoRiegoDB:
        """Crear nuevo evento de riego"""
        db_evento = EventoRiegoDB(
            dispositivo_id=evento.dispositivo_id,
            accion=evento.accion.value,
            duracion_segundos=evento.duracion_segundos,
            manual=evento.manual,
            timestamp=evento.timestamp or datetime.now(timezone.utc)
        )
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)
        logger.info(f"Evento de riego: {evento.accion.value}, dispositivo={evento.dispositivo_id}")
        return db_evento

    @staticmethod
    def obtener_ultimo_evento(db: Session, dispositivo_id: str = "sensor1") -> Optional[EventoRiegoDB]:
        """Obtener último evento de riego"""
        return db.query(EventoRiegoDB).filter(
            EventoRiegoDB.dispositivo_id == dispositivo_id
        ).order_by(EventoRiegoDB.timestamp.desc()).first()

    @staticmethod
    def obtener_historial(
        db: Session,
        dispositivo_id: str = "sensor1",
        limit: int = 100,
        offset: int = 0,
        inicio: Optional[datetime] = None,
        fin: Optional[datetime] = None,
    ) -> tuple[list[EventoRiegoDB], int]:
        """Obtener historial de eventos de riego"""
        query = db.query(EventoRiegoDB).filter(
            EventoRiegoDB.dispositivo_id == dispositivo_id
        )
        
        if inicio:
            query = query.filter(EventoRiegoDB.timestamp >= inicio)
        if fin:
            query = query.filter(EventoRiegoDB.timestamp <= fin)
        
        total = query.count()
        eventos = query.order_by(
            EventoRiegoDB.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        return eventos, total

    @staticmethod
    def obtener_tiempo_riego_total_hoy(db: Session, dispositivo_id: str = "sensor1") -> int:
        """Obtener tiempo total de riego hoy en segundos"""
        from datetime import timedelta
        
        hoy = datetime.now(timezone.utc).date()
        inicio_hoy = datetime.combine(hoy, datetime.min.time(), tzinfo=timezone.utc)
        fin_hoy = datetime.combine(hoy, datetime.max.time(), tzinfo=timezone.utc)
        
        from sqlalchemy import func
        
        resultado = db.query(func.sum(EventoRiegoDB.duracion_segundos)).filter(
            EventoRiegoDB.dispositivo_id == dispositivo_id,
            EventoRiegoDB.accion == "ON",
            EventoRiegoDB.timestamp >= inicio_hoy,
            EventoRiegoDB.timestamp <= fin_hoy
        ).scalar()
        
        return resultado or 0


class ConfiguracionService:
    """Servicio para gestionar configuración del sistema"""

    @staticmethod
    def obtener_configuracion(db: Session, dispositivo_id: str = "sensor1") -> ConfiguracionDB:
        """Obtener configuración de un dispositivo"""
        config = db.query(ConfiguracionDB).filter(
            ConfiguracionDB.dispositivo_id == dispositivo_id
        ).first()
        
        if not config:
            # Crear configuración por defecto
            config = ConfiguracionDB(dispositivo_id=dispositivo_id)
            db.add(config)
            db.commit()
            db.refresh(config)
            logger.info(f"Configuración por defecto creada para {dispositivo_id}")
        
        return config

    @staticmethod
    def actualizar_umbral(db: Session, dispositivo_id: str, umbral: int) -> ConfiguracionDB:
        """Actualizar umbral de humedad"""
        config = ConfiguracionService.obtener_configuracion(db, dispositivo_id)
        config.umbral_humedad = umbral
        config.actualizado = datetime.now(timezone.utc)
        db.commit()
        db.refresh(config)
        logger.info(f"Umbral actualizado para {dispositivo_id}: {umbral}%")
        return config

    @staticmethod
    def actualizar_intervalo(db: Session, dispositivo_id: str, intervalo: int) -> ConfiguracionDB:
        """Actualizar intervalo de lectura"""
        config = ConfiguracionService.obtener_configuracion(db, dispositivo_id)
        config.intervalo_lectura_min = intervalo
        config.actualizado = datetime.now(timezone.utc)
        db.commit()
        db.refresh(config)
        logger.info(f"Intervalo actualizado para {dispositivo_id}: {intervalo} min")
        return config


class ClimaService:
    """Servicio para gestionar pronósticos de clima"""

    @staticmethod
    def guardar_pronostico(
        db: Session,
        ciudad: str,
        fecha: datetime,
        lluvia_mm: float,
        temp_max: Optional[float] = None,
        temp_min: Optional[float] = None,
        humedad: Optional[int] = None,
        descripcion: Optional[str] = None,
    ) -> PronosticoClimaDB:
        """Guardar o actualizar pronóstico"""
        fecha_base = fecha
        if fecha_base.tzinfo is None:
            fecha_base = fecha_base.replace(tzinfo=timezone.utc)

        inicio_dia = fecha_base.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = fecha_base.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Verificar si ya existe
        pronostico = db.query(PronosticoClimaDB).filter(
            PronosticoClimaDB.ciudad == ciudad,
            PronosticoClimaDB.fecha.between(inicio_dia, fin_dia)
        ).first()
        
        if pronostico:
            # Actualizar
            pronostico.lluvia_esperada_mm = lluvia_mm
            pronostico.temperatura_max = temp_max
            pronostico.temperatura_min = temp_min
            pronostico.humedad_relativa = humedad
            pronostico.descripcion = descripcion
            pronostico.actualizado = datetime.now(timezone.utc)
        else:
            # Crear nuevo
            pronostico = PronosticoClimaDB(
                ciudad=ciudad,
                fecha=fecha_base,
                lluvia_esperada_mm=lluvia_mm,
                temperatura_max=temp_max,
                temperatura_min=temp_min,
                humedad_relativa=humedad,
                descripcion=descripcion
            )
            db.add(pronostico)
        
        db.commit()
        db.refresh(pronostico)
        return pronostico

    @staticmethod
    def obtener_pronostico_hoy(db: Session, ciudad: str) -> list[PronosticoClimaDB]:
        """Obtener pronóstico para hoy"""
        hoy = datetime.now(timezone.utc).date()
        inicio_hoy = datetime.combine(hoy, datetime.min.time(), tzinfo=timezone.utc)
        fin_hoy = datetime.combine(hoy, datetime.max.time(), tzinfo=timezone.utc)
        
        return db.query(PronosticoClimaDB).filter(
            PronosticoClimaDB.ciudad == ciudad,
            PronosticoClimaDB.fecha >= inicio_hoy,
            PronosticoClimaDB.fecha <= fin_hoy
        ).order_by(PronosticoClimaDB.fecha).all()

    @staticmethod
    def obtener_lluvia_proximas_horas(db: Session, ciudad: str, horas: int = 24) -> float:
        """Obtener total de lluvia esperada en las próximas horas"""
        from datetime import timedelta
        from sqlalchemy import func
        
        ahora = datetime.now(timezone.utc)
        limite = ahora + timedelta(hours=horas)
        
        resultado = db.query(func.sum(PronosticoClimaDB.lluvia_esperada_mm)).filter(
            PronosticoClimaDB.ciudad == ciudad,
            PronosticoClimaDB.fecha >= ahora,
            PronosticoClimaDB.fecha <= limite
        ).scalar()
        
        return resultado or 0.0
