"""Tests básicos para el backend"""
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestHealth:
    """Tests para health check"""
    
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "nombre" in response.json()
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "OK"


class TestSensores:
    """Tests para endpoints de sensores"""
    
    def test_crear_lectura(self):
        """Test crear lectura de sensor"""
        payload = {
            "humedad": 65.5,
            "dispositivo_id": "sensor1",
            "temperatura": 28.0
        }
        response = client.post("/api/sensores/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["humedad"] == 65.5
        assert data["dispositivo_id"] == "sensor1"


class TestRiego:
    """Tests para endpoints de riego"""
    
    def test_obtener_estado(self):
        """Test obtener estado de riego"""
        response = client.get("/api/riego/estado")
        assert response.status_code == 200
        data = response.json()
        assert "activo" in data
    
    def test_obtener_historial(self):
        """Test obtener historial de riego"""
        response = client.get("/api/riego/historial")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "eventos" in data


class TestConfiguracion:
    """Tests para endpoints de configuración"""
    
    def test_obtener_config(self):
        """Test obtener configuración"""
        response = client.get("/api/config/")
        assert response.status_code == 200
        data = response.json()
        assert "umbral_humedad" in data


class TestDashboard:
    """Tests para dashboard"""
    
    def test_obtener_dashboard(self):
        """Test obtener dashboard actual"""
        response = client.get("/api/dashboard/actual")
        assert response.status_code == 200
        data = response.json()
        assert "humedad_actual" in data
        assert "riego_activo" in data
