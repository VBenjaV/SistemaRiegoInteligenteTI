#!/usr/bin/env python
"""
Cliente Python para probar el Sistema de Riego Inteligente

Este script permite hacer pruebas manuales de los endpoints de la API
"""

import requests
import json
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8000"


class ClienteRiego:
    """Cliente para interactuar con la API de Riego"""
    
    def __init__(self, base_url: str = BASE_URL, verbose: bool = True):
        self.base_url = base_url
        self.verbose = verbose
        self.session = requests.Session()
    
    def _print(self, msg: str):
        if self.verbose:
            print(msg)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Hacer una solicitud HTTP"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            elif method.upper() == "PUT":
                response = self.session.put(url, **kwargs)
            else:
                raise ValueError(f"Método {method} no soportado")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._print(f"❌ Error: {e}")
            return None
    
    # ========================================================================
    # SENSORES
    # ========================================================================
    
    def crear_lectura(self, humedad: float, dispositivo_id: str = "sensor1", 
                     temperatura: Optional[float] = None) -> dict:
        """Crear una nueva lectura de sensor"""
        payload = {
            "humedad": humedad,
            "dispositivo_id": dispositivo_id,
        }
        if temperatura is not None:
            payload["temperatura"] = temperatura
        
        self._print(f"\n📊 Creando lectura: humedad={humedad}%")
        response = self._request("POST", "/api/sensores/", json=payload)
        
        if response:
            self._print(f"✅ Lectura guardada - ID: {response.get('id')}")
        return response
    
    def obtener_lectura_actual(self, dispositivo_id: str = "sensor1") -> dict:
        """Obtener última lectura del sensor"""
        self._print(f"\n🔍 Obteniendo lectura actual...")
        response = self._request(
            "GET", "/api/sensores/actual",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            humedad = response.get("humedad")
            self._print(f"✅ Lectura actual: {humedad}%")
        return response
    
    def obtener_historial(self, dispositivo_id: str = "sensor1", dias: int = 1,
                         limit: int = 50) -> dict:
        """Obtener historial de lecturas"""
        self._print(f"\n📈 Obteniendo historial ({dias} días)...")
        response = self._request(
            "GET", "/api/sensores/historial",
            params={
                "dispositivo_id": dispositivo_id,
                "dias": dias,
                "limit": limit
            }
        )
        
        if response:
            total = response.get("total", 0)
            self._print(f"✅ Total de lecturas: {total}")
        return response
    
    def obtener_promedio(self, dispositivo_id: str = "sensor1", 
                        minutos: int = 60) -> dict:
        """Obtener promedio de humedad"""
        self._print(f"\n📊 Calculando promedio ({minutos} min)...")
        response = self._request(
            "GET", "/api/sensores/promedio",
            params={
                "dispositivo_id": dispositivo_id,
                "minutos": minutos
            }
        )
        
        if response:
            promedio = response.get("promedio_humedad")
            self._print(f"✅ Promedio: {promedio}%")
        return response
    
    # ========================================================================
    # RIEGO
    # ========================================================================
    
    def obtener_estado_riego(self, dispositivo_id: str = "sensor1") -> dict:
        """Obtener estado actual del riego"""
        self._print(f"\n💧 Obteniendo estado del riego...")
        response = self._request(
            "GET", "/api/riego/estado",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            activo = response.get("activo")
            estado = "🟢 ACTIVO" if activo else "🔴 INACTIVO"
            self._print(f"✅ Estado: {estado}")
        return response
    
    def evaluar_riego(self, dispositivo_id: str = "sensor1") -> dict:
        """Ejecutar lógica de riego inteligente"""
        self._print(f"\n🤖 Evaluando lógica de riego...")
        response = self._request(
            "POST", "/api/riego/evaluar",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            decision = response.get("decision")
            motivo = response.get("motivo")
            self._print(f"✅ Decisión: {decision}")
            self._print(f"   Motivo: {motivo}")
        return response
    
    def forzar_riego_on(self, dispositivo_id: str = "sensor1",
                       duracion_segundos: int = 300) -> dict:
        """Activar riego manualmente"""
        self._print(f"\n🟢 Activando riego ({duracion_segundos}s)...")
        payload = {
            "accion": "ON",
            "duracion_segundos": duracion_segundos,
            "dispositivo_id": dispositivo_id
        }
        response = self._request("POST", "/api/riego/forzar-on", json=payload)
        
        if response and response.get("exito"):
            self._print(f"✅ Riego activado")
        return response
    
    def forzar_riego_off(self, dispositivo_id: str = "sensor1") -> dict:
        """Desactivar riego manualmente"""
        self._print(f"\n🔴 Desactivando riego...")
        response = self._request(
            "POST", "/api/riego/forzar-off",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response and response.get("exito"):
            self._print(f"✅ Riego desactivado")
        return response
    
    def obtener_historial_riego(self, dispositivo_id: str = "sensor1",
                               dias: int = 1) -> dict:
        """Obtener historial de eventos de riego"""
        self._print(f"\n📋 Obteniendo historial de riego...")
        response = self._request(
            "GET", "/api/riego/historial",
            params={
                "dispositivo_id": dispositivo_id,
                "dias": dias
            }
        )
        
        if response:
            total = response.get("total", 0)
            self._print(f"✅ Total eventos: {total}")
        return response
    
    def obtener_tiempo_riego_hoy(self, dispositivo_id: str = "sensor1") -> dict:
        """Obtener tiempo de riego hoy"""
        self._print(f"\n⏱️ Obteniendo tiempo de riego hoy...")
        response = self._request(
            "GET", "/api/riego/tiempo-total-hoy",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            minutos = response.get("tiempo_total_minutos", 0)
            self._print(f"✅ Tiempo total: {minutos} minutos")
        return response
    
    # ========================================================================
    # CONFIGURACIÓN
    # ========================================================================
    
    def obtener_config(self, dispositivo_id: str = "sensor1") -> dict:
        """Obtener configuración"""
        self._print(f"\n⚙️ Obteniendo configuración...")
        response = self._request(
            "GET", "/api/config/",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            umbral = response.get("umbral_humedad")
            self._print(f"✅ Umbral: {umbral}%")
        return response
    
    def actualizar_umbral(self, umbral: int, 
                         dispositivo_id: str = "sensor1") -> dict:
        """Actualizar umbral de humedad"""
        self._print(f"\n⚙️ Actualizando umbral a {umbral}%...")
        payload = {
            "umbral_humedad": umbral,
            "dispositivo_id": dispositivo_id
        }
        response = self._request("PUT", "/api/config/umbral", json=payload)
        
        if response:
            self._print(f"✅ Umbral actualizado")
        return response
    
    # ========================================================================
    # CLIMA
    # ========================================================================
    
    def obtener_pronostico(self, ciudad: str = "Mexico City") -> dict:
        """Obtener pronóstico meteorológico"""
        self._print(f"\n🌦️ Obteniendo pronóstico para {ciudad}...")
        response = self._request(
            "GET", "/api/clima/pronostico",
            params={"ciudad": ciudad}
        )
        
        if response:
            lluvia = response.get("lluvia_pronostico", {}).get("lluvia_total_mm")
            self._print(f"✅ Lluvia esperada: {lluvia}mm")
        return response
    
    def obtener_lluvia_24h(self, ciudad: str = "Mexico City") -> dict:
        """Obtener lluvia esperada en 24h"""
        self._print(f"\n🌧️ Obteniendo lluvia 24h...")
        response = self._request(
            "GET", "/api/clima/lluvia-24h",
            params={"ciudad": ciudad}
        )
        
        if response:
            lluvia = response.get("lluvia_24h_mm")
            se_riega = response.get("se_recomienda_riego")
            self._print(f"✅ Lluvia 24h: {lluvia}mm - Riego: {'SÍ' if se_riega else 'NO'}")
        return response
    
    # ========================================================================
    # DASHBOARD
    # ========================================================================
    
    def obtener_dashboard(self, dispositivo_id: str = "sensor1") -> dict:
        """Obtener dashboard en tiempo real"""
        self._print(f"\n📊 Obteniendo dashboard...")
        response = self._request(
            "GET", "/api/dashboard/actual",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            humedad = response.get("humedad_actual")
            riego = response.get("riego_activo")
            self._print(f"✅ Humedad: {humedad}% | Riego: {'SÍ' if riego else 'NO'}")
        return response
    
    def obtener_resumen(self, dispositivo_id: str = "sensor1") -> dict:
        """Obtener resumen del sistema"""
        self._print(f"\n📋 Obteniendo resumen...")
        response = self._request(
            "GET", "/api/dashboard/resumen",
            params={"dispositivo_id": dispositivo_id}
        )
        
        if response:
            self._print(f"✅ Resumen obtenido")
        return response


# ============================================================================
# MAIN - DEMOSTRACIÓN
# ============================================================================

def demostration():
    """Realizar una demostración completa"""
    
    cliente = ClienteRiego()
    
    print("=" * 60)
    print("🌾 SISTEMA DE RIEGO INTELIGENTE - CLIENTE DE PRUEBA")
    print("=" * 60)
    
    # Verificar que la API está disponible
    print("\n🔍 Verificando conexión a API...")
    try:
        respuesta = cliente.session.get(f"{BASE_URL}/health")
        if respuesta.status_code == 200:
            print("✅ Conexión OK")
        else:
            print("❌ Error de conexión")
            return
    except Exception as e:
        print(f"❌ No se puede conectar a {BASE_URL}")
        print(f"   Error: {e}")
        return
    
    # Demostración
    dispositivo = "sensor1"
    
    # 1. Crear algunas lecturas
    print("\n" + "=" * 60)
    print("1️⃣ CREANDO LECTURAS DE SENSOR")
    print("=" * 60)
    
    cliente.crear_lectura(65.5, dispositivo, 28.0)
    cliente.crear_lectura(68.2, dispositivo, 28.5)
    cliente.crear_lectura(45.0, dispositivo, 29.0)
    
    # 2. Obtener última lectura
    print("\n" + "=" * 60)
    print("2️⃣ LECTURA ACTUAL")
    print("=" * 60)
    cliente.obtener_lectura_actual(dispositivo)
    
    # 3. Estadísticas
    print("\n" + "=" * 60)
    print("3️⃣ ESTADÍSTICAS")
    print("=" * 60)
    cliente.obtener_promedio(dispositivo, 60)
    
    # 4. Configuración
    print("\n" + "=" * 60)
    print("4️⃣ CONFIGURACIÓN")
    print("=" * 60)
    cliente.obtener_config(dispositivo)
    
    # 5. Estado de riego
    print("\n" + "=" * 60)
    print("5️⃣ ESTADO DE RIEGO")
    print("=" * 60)
    cliente.obtener_estado_riego(dispositivo)
    
    # 6. Evaluar lógica
    print("\n" + "=" * 60)
    print("6️⃣ EVALUAR LÓGICA DE RIEGO")
    print("=" * 60)
    cliente.evaluar_riego(dispositivo)
    
    # 7. Clima
    print("\n" + "=" * 60)
    print("7️⃣ INFORMACIÓN METEOROLÓGICA")
    print("=" * 60)
    cliente.obtener_lluvia_24h()
    
    # 8. Dashboard
    print("\n" + "=" * 60)
    print("8️⃣ DASHBOARD")
    print("=" * 60)
    cliente.obtener_dashboard(dispositivo)
    
    # 9. Control manual
    print("\n" + "=" * 60)
    print("9️⃣ CONTROL MANUAL")
    print("=" * 60)
    cliente.forzar_riego_on(dispositivo, 60)
    cliente.obtener_estado_riego(dispositivo)
    cliente.forzar_riego_off(dispositivo)
    
    print("\n" + "=" * 60)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    demostration()
