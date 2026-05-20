from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from app.config import settings

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LecturaSensorDB(Base):
    """Modelo de base de datos para lecturas de sensores"""
    __tablename__ = "lecturas_sensores"
    __table_args__ = (
        Index("ix_lecturas_sensores_dispositivo_timestamp", "dispositivo_id", "timestamp"),
    )

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(String(50), index=True, nullable=False)
    humedad = Column(Float, nullable=False)
    temperatura = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    creado = Column(DateTime(timezone=True), default=utcnow)


class EventoRiegoDB(Base):
    """Modelo de base de datos para eventos de riego"""
    __tablename__ = "eventos_riego"
    __table_args__ = (
        Index("ix_eventos_riego_dispositivo_timestamp", "dispositivo_id", "timestamp"),
    )

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(String(50), index=True, nullable=False)
    accion = Column(String(10), nullable=False)  # ON/OFF
    duracion_segundos = Column(Integer, default=300)
    manual = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    creado = Column(DateTime(timezone=True), default=utcnow)


class ConfiguracionDB(Base):
    """Modelo alineado con Supabase: dispositivo_id es PK."""
    __tablename__ = "configuracion"

    dispositivo_id = Column(String(50), primary_key=True, index=True, nullable=False)
    umbral_humedad = Column(Integer, default=40)
    intervalo_lectura_min = Column(Integer, default=5)
    lluvia_minima_mm = Column(Float, default=5.0)
    horas_pronostico = Column(Integer, default=24)
    actualizado = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    creado = Column(DateTime(timezone=True), default=utcnow)


class PronosticoClimaDB(Base):
    """Modelo de base de datos para pronósticos meteorológicos"""
    __tablename__ = "pronostico_clima"
    __table_args__ = (
        Index("ix_pronostico_ciudad_fecha", "ciudad", "fecha"),
    )

    id = Column(Integer, primary_key=True, index=True)
    ciudad = Column(String(100), index=True, nullable=False)
    fecha = Column(DateTime(timezone=True), index=True, nullable=False)
    lluvia_esperada_mm = Column(Float, default=0.0)
    temperatura_max = Column(Float, nullable=True)
    temperatura_min = Column(Float, nullable=True)
    humedad_relativa = Column(Integer, nullable=True)
    descripcion = Column(String(200), nullable=True)
    actualizado = Column(DateTime(timezone=True), default=utcnow)


# Configuracion de conexion a BD
DATABASE_URL = settings.sqlalchemy_database_url

if DATABASE_URL.startswith("sqlite"):
    raise ValueError("SQLite no permitido; use SUPABASE_DB_URL")

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependencia para obtener sesión de BD"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar base de datos - crear tablas"""
    Base.metadata.create_all(bind=engine)
