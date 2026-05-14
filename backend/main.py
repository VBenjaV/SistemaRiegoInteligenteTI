"""Aplicación principal de FastAPI"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.api import router
from app.services import init_mqtt, close_mqtt

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    init_db()
    logger.info("Base de datos inicializada")
    
    try:
        await init_mqtt()
        logger.info("MQTT inicializado correctamente")
    except Exception as e:
        logger.warning(f"MQTT no disponible: {e}. La aplicación funcionará sin MQTT.")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    try:
        await close_mqtt()
    except:
        pass
    logger.info("MQTT cerrado")


# Crear aplicación
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router)


# Endpoints raíz
@app.get("/", tags=["Info"])
async def root():
    """Endpoint raíz - información de la API"""
    return {
        "nombre": settings.api_title,
        "version": settings.api_version,
        "descripcion": settings.api_description,
        "documentacion": "/docs"
    }


@app.get("/health", tags=["Info"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "servicio": "Sistema de Riego Inteligente"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info" if not settings.debug else "debug"
    )
