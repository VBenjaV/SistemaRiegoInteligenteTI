from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class LecturaSensorDB(Base):
    """Modelo de base de datos para lecturas de sensores"""
    __tablename__ = "lecturas_sensores"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(String(50), index=True)
    humedad = Column(Float, nullable=False)
    temperatura = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    creado = Column(DateTime, default=datetime.utcnow)


class EventoRiegoDB(Base):
    """Modelo de base de datos para eventos de riego"""
    __tablename__ = "eventos_riego"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(String(50), index=True)
    accion = Column(String(10), nullable=False)  # ON/OFF
    duracion_segundos = Column(Integer, default=300)
    manual = Column(Boolean, default=False)
    timestamp = Column(DateTime, nullable=False)
    creado = Column(DateTime, default=datetime.utcnow)


class ConfiguracionDB(Base):
    """Modelo de base de datos para configuración"""
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(String(50), unique=True, index=True)
    umbral_humedad = Column(Integer, default=40)
    intervalo_lectura_min = Column(Integer, default=5)
    lluvia_minima_mm = Column(Float, default=5.0)
    horas_pronostico = Column(Integer, default=24)
    actualizado = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado = Column(DateTime, default=datetime.utcnow)


class PronosticoClimaDB(Base):
    """Modelo de base de datos para pronósticos meteorológicos"""
    __tablename__ = "pronostico_clima"

    id = Column(Integer, primary_key=True, index=True)
    ciudad = Column(String(100), index=True)
    fecha = Column(DateTime, index=True)
    lluvia_esperada_mm = Column(Float, default=0.0)
    temperatura_max = Column(Float, nullable=True)
    temperatura_min = Column(Float, nullable=True)
    humedad_relativa = Column(Integer, nullable=True)
    descripcion = Column(String(200), nullable=True)
    actualizado = Column(DateTime, default=datetime.utcnow)


# Configuración de conexión a BD
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./riego.db")

# Para SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # Para PostgreSQL u otras BD
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
