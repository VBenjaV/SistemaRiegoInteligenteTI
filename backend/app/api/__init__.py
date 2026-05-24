"""Routers - Exporte centralizado"""
from fastapi import APIRouter
from . import sensores, riego, configuracion, clima, dashboard
# auth endpoints están en main.py directamente para login simple

# Router principal
router = APIRouter()

# Incluir todos los routers
# router.include_router(auth.router)  # No necesario - endpoints en main.py
router.include_router(sensores.router)
router.include_router(riego.router)
router.include_router(configuracion.router)
router.include_router(clima.router)
router.include_router(dashboard.router)

__all__ = ["router"]
