"""Servicio de autenticación con Supabase"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from app.config import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    """Datos extraídos del token JWT"""
    sub: str  # user_id
    email: Optional[str] = None
    iat: Optional[int] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Request para registro"""
    email: EmailStr
    password: str
    nombre: Optional[str] = None


class AuthResponse(BaseModel):
    """Response de autenticación"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: str
    email: str


class SupabaseAuthService:
    """Servicio de autenticación con Supabase"""

    def __init__(self):
        """Inicializar el cliente de Supabase"""
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridas")
        
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info(f"Supabase Auth Service inicializado: {settings.supabase_url}")

    def register(self, email: str, password: str, nombre: Optional[str] = None) -> dict:
        """
        Registrar un nuevo usuario en Supabase
        
        Args:
            email: Email del usuario
            password: Contraseña
            nombre: Nombre del usuario (opcional)
            
        Returns:
            dict con user_id y email
            
        Raises:
            Exception: Si ocurre un error durante el registro
        """
        try:
            # Supabase Auth maneja el registro de usuarios
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                logger.info(f"Usuario registrado: {email}")
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "mensaje": "Usuario registrado. Por favor, verifica tu email."
                }
            else:
                raise Exception("Error en el registro del usuario")
                
        except Exception as e:
            logger.error(f"Error registrando usuario {email}: {str(e)}")
            raise

    def login(self, email: str, password: str) -> AuthResponse:
        """
        Autenticar usuario con email y contraseña
        
        Args:
            email: Email del usuario
            password: Contraseña
            
        Returns:
            AuthResponse con tokens
            
        Raises:
            Exception: Si las credenciales son inválidas
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.session:
                logger.info(f"Usuario autenticado: {email}")
                return AuthResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    user_id=response.user.id,
                    email=response.user.email
                )
            else:
                raise Exception("No se pudo autenticar el usuario")
                
        except Exception as e:
            logger.error(f"Error autenticando usuario {email}: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refrescar el token de acceso
        
        Args:
            refresh_token: Token de refresco
            
        Returns:
            AuthResponse con nuevo access token
            
        Raises:
            Exception: Si el refresh token es inválido
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                logger.info(f"Token refrescado para usuario: {response.user.id}")
                return AuthResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    user_id=response.user.id,
                    email=response.user.email
                )
            else:
                raise Exception("No se pudo refrescar el token")
                
        except Exception as e:
            logger.error(f"Error refrescando token: {str(e)}")
            raise

    def verify_token(self, token: str) -> TokenData:
        """
        Verificar y decodificar un token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            TokenData con información del usuario
            
        Raises:
            JWTError: Si el token es inválido o expiró
        """
        try:
            # Decodificar el token con la clave secreta de Supabase
            # Nota: En producción, se debe usar la clave pública de Supabase
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret or settings.supabase_key,
                algorithms=["HS256"]
            )
            
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None:
                raise JWTError("No user_id en token")
            
            token_data = TokenData(
                sub=user_id,
                email=email,
                iat=payload.get("iat"),
                exp=payload.get("exp")
            )
            
            return token_data
            
        except JWTError as e:
            logger.error(f"Error verificando token: {str(e)}")
            raise

    def get_current_user(self, token: str) -> dict:
        """
        Obtener información del usuario actual del token
        
        Args:
            token: Token JWT
            
        Returns:
            dict con información del usuario
            
        Raises:
            JWTError: Si el token es inválido
        """
        try:
            token_data = self.verify_token(token)
            return {
                "user_id": token_data.sub,
                "email": token_data.email
            }
        except JWTError:
            raise


# Instancia global del servicio
def get_auth_service() -> SupabaseAuthService:
    """Obtener instancia del servicio de autenticación"""
    return SupabaseAuthService()
