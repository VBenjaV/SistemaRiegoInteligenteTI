"""API endpoints para autenticación"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.auth_service import (
    get_auth_service,
    SupabaseAuthService,
    LoginRequest,
    RegisterRequest,
    AuthResponse
)
from app.api.auth_deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token"""
    refresh_token: str


class LoginResponse(BaseModel):
    """Response de login"""
    access_token: str
    refresh_token: str | None = None
    token_type: str
    user_id: str
    email: str


class RegisterResponse(BaseModel):
    """Response de registro"""
    user_id: str
    email: str
    mensaje: str


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """
    Registrar un nuevo usuario
    
    - **email**: Email del usuario (debe ser único)
    - **password**: Contraseña (mínimo 8 caracteres)
    - **nombre**: Nombre del usuario (opcional)
    """
    try:
        result = auth_service.register(
            email=request.email,
            password=request.password,
            nombre=request.nombre
        )
        return result
        
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        
        # Manejo de errores comunes de Supabase
        error_msg = str(e).lower()
        
        if "already exists" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el registro: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """
    Autenticar un usuario con email y contraseña
    
    - **email**: Email registrado
    - **password**: Contraseña
    
    Retorna un access token que debe ser incluido en el header Authorization
    """
    try:
        response = auth_service.login(
            email=request.email,
            password=request.password
        )
        return response
        
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """
    Refrescar el access token usando el refresh token
    
    - **refresh_token**: Token de refresco obtenido en el login
    """
    try:
        response = auth_service.refresh_token(request.refresh_token)
        return response
        
    except Exception as e:
        logger.error(f"Error refrescando token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtener información del usuario actual autenticado
    
    Requiere el access token en el header Authorization: Bearer <token>
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "mensaje": "Usuario autenticado correctamente"
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout del usuario actual
    
    Nota: En el cliente, también debe eliminar el access_token y refresh_token del localStorage
    """
    logger.info(f"Usuario {current_user['email']} ha cerrado sesión")
    return {
        "mensaje": "Sesión cerrada correctamente"
    }
