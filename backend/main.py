"""Aplicación principal de FastAPI"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from app.config import settings
# from app.db.database import init_db  # No necesario para login simple
from app.db.mongo import init_mongo, close_mongo
from app.api import router
from app.services import init_mqtt, close_mqtt, get_mqtt_client

# Importar Supabase para autenticación simple
try:
    from supabase import create_client
except ImportError:
    pass

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Modelos para autenticación
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Mínimo 8 caracteres")


class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    email: str


def _mensaje_error_auth(exc: Exception) -> str:
    """Traduce errores de Supabase Auth a mensajes claros para el frontend."""
    msg = getattr(exc, "message", None) or str(exc)
    if hasattr(exc, "to_dict"):
        try:
            data = exc.to_dict()
            msg = data.get("message") or data.get("msg") or msg
        except Exception:
            pass
    lower = str(msg).lower()
    if "already" in lower or "registered" in lower or "exists" in lower:
        return "Este email ya está registrado"
    if "password" in lower:
        return f"Contraseña no válida: {msg}"
    if "invalid" in lower and "email" in lower:
        return "El correo electrónico no es válido"
    if "signup" in lower and "disabled" in lower:
        return "El registro está deshabilitado en Supabase (Authentication → Providers → Email)"
    if "rate" in lower or "limit" in lower or "429" in lower:
        return (
            "Límite de envío de correos de Supabase alcanzado. "
            "Espera 30–60 minutos, usa otro email o desactiva «Confirm email» "
            "en Authentication → Providers → Email."
        )
    return str(msg)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    # try:
    #     init_db()
    #     logger.info("Base de datos PostgreSQL inicializada")
    # except Exception as e:
    #     logger.error("PostgreSQL no disponible al inicio: %s", e)

    init_mongo()
    logger.info("MongoDB inicializado")

    try:
        await init_mqtt()
        logger.info("AWS IoT Core (MQTT) inicializado")
    except Exception as e:
        logger.error("MQTT no disponible al inicio: %s", e)
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    await close_mqtt()
    close_mongo()
    logger.info("Conexiones cerradas")


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


# ============ ENDPOINTS DE AUTENTICACIÓN ============

@app.post("/auth/register", response_model=dict, tags=["Auth"])
async def register(request: RegisterRequest):
    """Registrar un nuevo usuario en Supabase"""
    if not settings.supabase_url or not settings.supabase_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase no configurado"
        )
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_key)
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if response.user:
            return {
                "user_id": response.user.id,
                "email": response.user.email,
                "mensaje": "Registro exitoso. Verifica tu email para confirmar."
            }
        else:
            raise Exception("Error en el registro")
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid api key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Clave de Supabase incorrecta. En backend/.env usa la clave "
                    "'anon' / 'publishable' (eyJ...), no la 'service_role' (sb_secret_...)."
                ),
            )
        logger.error("Error registrando usuario: %s", e)
        detail = _mensaje_error_auth(e)
        status_code = (
            status.HTTP_429_TOO_MANY_REQUESTS
            if "rate" in str(e).lower() or "429" in str(e).lower()
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=detail)


@app.post("/auth/login", response_model=AuthResponse, tags=["Auth"])
async def login(request: LoginRequest):
    """Autenticar usuario con email y contraseña"""
    if not settings.supabase_url or not settings.supabase_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase no configurado"
        )
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_key)
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.session and response.user:
            return AuthResponse(
                access_token=response.session.access_token,
                user_id=response.user.id,
                email=response.user.email
            )
        else:
            raise Exception("Error en la autenticación")
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid api key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Clave de Supabase incorrecta. En backend/.env usa la clave "
                    "'anon' / 'publishable' (eyJ...), no la 'service_role' (sb_secret_...)."
                ),
            )
        logger.error(f"Error autenticando usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )


@app.get("/health", tags=["Info"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "servicio": "Sistema de Riego Inteligente"
    }


@app.get("/api/debug/mqtt", tags=["Info"])
async def mqtt_status():
    """Estado de conexión MQTT y topics configurados."""
    client = get_mqtt_client()
    return {
        "conectado": client.is_connected(),
        "endpoint": settings.mqtt_host,
        "topic_suscrito": settings.mqtt_topic_subscribe,
        "topic_publicar": settings.mqtt_topic_publish,
        "nota": "Si conectado=true pero no hay lecturas, revisa la policy IoT del certificado en IotCore/",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info" if not settings.debug else "debug"
    )
