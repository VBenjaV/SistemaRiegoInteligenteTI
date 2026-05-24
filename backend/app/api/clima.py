"""API endpoints para clima"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.config import settings
from app.models import InformacionClima, PronosticoClima
from app.services.weather_service import get_weather_service
from app.services.database_service import ClimaService

router = APIRouter(prefix="/api/clima", tags=["Clima"])


@router.get(
    "/pronostico",
    response_model=dict,
    summary="Obtener pronóstico meteorológico",
    description="Retorna pronóstico de lluvia y clima para decisiones de riego"
)
async def obtener_pronostico(
    ciudad: str = Query(settings.weather_city, description="Nombre de la ciudad"),
):
    """Obtener pronóstico meteorológico"""
    weather_service = get_weather_service()
    
    if not weather_service.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de clima no configurado"
        )
    
    weather_info = weather_service.get_complete_weather_info(ciudad)
    
    return {
        "ciudad": ciudad,
        "clima_actual": weather_info["clima_actual"],
        "lluvia_pronostico": weather_info["lluvia_pronostico"],
        "se_debe_regar": weather_info["se_debe_regar"],
        "umbral_lluvia_mm": settings.weather_rain_threshold_mm,
        "horas_pronostico": settings.weather_forecast_hours,
        "actualizado": weather_info["actualizado"]
    }


@router.get(
    "/actual",
    response_model=InformacionClima,
    summary="Obtener clima actual",
    description="Retorna clima actual de una ciudad"
)
async def obtener_clima_actual(
    ciudad: str = Query(settings.weather_city, description="Nombre de la ciudad"),
):
    """Obtener clima actual"""
    weather_service = get_weather_service()
    
    if not weather_service.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de clima no configurado"
        )
    
    current_data = weather_service.get_current_weather(ciudad)
    
    if not current_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró información para {ciudad}"
        )
    
    main = current_data.get("main", {})
    weather = current_data.get("weather", [{}])[0]
    
    from datetime import datetime
    return InformacionClima(
        ciudad=current_data.get("name", ciudad),
        temperatura=main.get("temp", 0),
        humedad_relativa=main.get("humidity", 0),
        descripcion=weather.get("description", "").capitalize(),
        lluvia_hoy_mm=current_data.get("rain", {}).get("1h", 0),
        pronostico_lluvia_24h_mm=0.0,  # Requeriría llamada adicional
        actualizado=datetime.utcnow()
    )


@router.post(
    "/actualizar-pronostico",
    response_model=dict,
    summary="Actualizar pronóstico en base de datos",
    description="Obtiene pronóstico actual y lo almacena"
)
async def actualizar_pronostico(
    ciudad: str = Query(settings.weather_city, description="Nombre de la ciudad"),
    db: Session = Depends(get_db)
):
    """Actualizar pronóstico en BD"""
    weather_service = get_weather_service()
    
    if not weather_service.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de clima no configurado"
        )
    
    forecast_data = weather_service.get_forecast(ciudad, settings.weather_forecast_hours)
    
    if not forecast_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error obtiendo pronóstico"
        )
    
    # Guardar en BD
    pronosticos_guardados = 0
    from datetime import datetime
    
    for item in forecast_data.get("list", []):
        fecha = datetime.fromtimestamp(item["dt"])
        lluvia_mm = item.get("rain", {}).get("3h", 0)
        main = item.get("main", {})
        
        ClimaService.guardar_pronostico(
            db,
            ciudad=ciudad,
            fecha=fecha,
            lluvia_mm=lluvia_mm,
            temp_max=main.get("temp_max"),
            temp_min=main.get("temp_min"),
            humedad=main.get("humidity"),
            descripcion=item.get("weather", [{}])[0].get("description")
        )
        pronosticos_guardados += 1
    
    return {
        "exito": True,
        "ciudad": ciudad,
        "pronosticos_guardados": pronosticos_guardados,
        "actualizado": datetime.utcnow().isoformat() + "Z"
    }


@router.get(
    "/lluvia-24h",
    response_model=dict,
    summary="Lluvia esperada próximas 24 horas",
    description="Retorna total de lluvia esperada en las próximas 24 horas"
)
async def obtener_lluvia_24h(
    ciudad: str = Query(settings.weather_city, description="Nombre de la ciudad"),
    db: Session = Depends(get_db)
):
    """Obtener lluvia esperada en 24 horas"""
    lluvia_total = ClimaService.obtener_lluvia_proximas_horas(
        db, ciudad, horas=24
    )
    
    from datetime import datetime
    return {
        "ciudad": ciudad,
        "lluvia_24h_mm": round(lluvia_total, 2),
        "umbral_riego_mm": settings.weather_rain_threshold_mm,
        "se_recomienda_riego": lluvia_total < settings.weather_rain_threshold_mm,
        "consultado": datetime.utcnow().isoformat() + "Z"
    }
