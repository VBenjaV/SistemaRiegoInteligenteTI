"""Dependencias y middleware de autenticación"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError
from app.services.auth_service import get_auth_service, SupabaseAuthService
import logging

logger = logging.getLogger(__name__)

# Esquema de seguridad Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> dict:
    """
    Dependency para extraer y verificar el token JWT del header Authorization
    
    Args:
        credentials: Credenciales del header Authorization
        
    Returns:
        dict con información del usuario (user_id, email)
        
    Raises:
        HTTPException: Si el token es inválido o expiró
    """
    token = credentials.credentials
    
    try:
        auth_service = get_auth_service()
        user = auth_service.get_current_user(token)
        return user
        
    except JWTError as e:
        logger.error(f"Token inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error verificando token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_auth_service_dep() -> SupabaseAuthService:
    """Dependency para obtener el servicio de autenticación"""
    return get_auth_service()
