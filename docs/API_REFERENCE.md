"""Documentación de API endpoints"""

# Sistema de Riego Inteligente - Referencia de API

## Base URL
```
http://localhost:8000
```

## Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints por Categoría

### 📡 SENSORES

#### POST /api/sensores/
Crear una nueva lectura de sensor

**Request:**
```json
{
  "humedad": 65.5,
  "dispositivo_id": "sensor1",
  "temperatura": 28.5
}
```

**Response:** 201
```json
{
  "id": 1,
  "humedad": 65.5,
  "dispositivo_id": "sensor1",
  "temperatura": 28.5,
  "timestamp": "2026-05-14T10:30:00Z",
  "creado": "2026-05-14T10:30:00Z"
}
```

---

#### GET /api/sensores/actual
Obtener la última lectura del sensor

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1"): ID del dispositivo

**Response:** 200
```json
{
  "id": 1,
  "humedad": 65.5,
  "dispositivo_id": "sensor1",
  "temperatura": 28.5,
  "timestamp": "2026-05-14T10:30:00Z",
  "creado": "2026-05-14T10:30:00Z"
}
```

---

#### GET /api/sensores/historial
Obtener historial de lecturas

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")
- `limit` (integer, default: 100, max: 1000)
- `offset` (integer, default: 0)
- `dias` (integer, optional): Últimos N días

**Response:** 200
```json
{
  "total": 150,
  "lecturas": [...],
  "inicio": "2026-05-10T00:00:00Z",
  "fin": "2026-05-14T23:59:59Z"
}
```

---

#### GET /api/sensores/promedio
Obtener promedio de humedad

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")
- `minutos` (integer, default: 60, min: 5, max: 1440)

**Response:** 200
```json
{
  "dispositivo_id": "sensor1",
  "promedio_humedad": 62.35,
  "periodo_minutos": 60,
  "calculado": "2026-05-14T10:30:00Z"
}
```

---

### 🚰 RIEGO

#### GET /api/riego/estado
Obtener estado actual del riego

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "activo": true,
  "duracion_restante_segundos": 250,
  "ultim_evento": {
    "id": 5,
    "dispositivo_id": "sensor1",
    "accion": "ON",
    "duracion_segundos": 300,
    "manual": false,
    "timestamp": "2026-05-14T10:30:00Z",
    "creado": "2026-05-14T10:30:00Z"
  },
  "ultima_lectura_humedad": 65.5
}
```

---

#### POST /api/riego/evaluar
Ejecutar lógica de riego inteligente

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "timestamp": "2026-05-14T10:30:00Z",
  "humedad_actual": 65.5,
  "umbral": 40,
  "lluvia_esperada": 2.5,
  "decision": "REGAR",
  "accion_tomada": "ON",
  "motivo": "Humedad 65.5% < umbral 40%, lluvia esperada 2.5mm"
}
```

---

#### POST /api/riego/forzar-on
Activar riego manualmente

**Request:**
```json
{
  "accion": "ON",
  "duracion_segundos": 300,
  "dispositivo_id": "sensor1"
}
```

**Response:** 200
```json
{
  "exito": true,
  "mensaje": "Riego activado manualmente",
  "evento_id": 6
}
```

---

#### POST /api/riego/forzar-off
Desactivar riego manualmente

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "exito": true,
  "mensaje": "Riego desactivado manualmente",
  "evento_id": 7
}
```

---

#### GET /api/riego/historial
Obtener historial de eventos de riego

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")
- `limit` (integer, default: 50)
- `offset` (integer, default: 0)
- `dias` (integer, optional)

**Response:** 200
```json
{
  "total": 25,
  "eventos": [...],
  "dispositivo_id": "sensor1",
  "periodo": {
    "inicio": null,
    "fin": null
  }
}
```

---

#### GET /api/riego/tiempo-total-hoy
Tiempo total de riego hoy

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "dispositivo_id": "sensor1",
  "fecha": "2026-05-14",
  "tiempo_total_segundos": 1800,
  "tiempo_total_horas": 0.5,
  "tiempo_total_minutos": 30.0
}
```

---

### ⚙️ CONFIGURACIÓN

#### GET /api/config/
Obtener configuración actual

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "id": 1,
  "dispositivo_id": "sensor1",
  "umbral_humedad": 40,
  "intervalo_lectura_min": 5,
  "lluvia_minima_mm": 5.0,
  "horas_pronostico": 24,
  "actualizado": "2026-05-14T10:30:00Z",
  "creado": "2026-05-14T10:30:00Z"
}
```

---

#### PUT /api/config/umbral
Actualizar umbral de humedad

**Request:**
```json
{
  "umbral_humedad": 45,
  "dispositivo_id": "sensor1"
}
```

**Response:** 200
```json
{
  "id": 1,
  "dispositivo_id": "sensor1",
  "umbral_humedad": 45,
  ...
}
```

---

#### PUT /api/config/intervalo
Actualizar intervalo de lectura

**Request:**
```json
{
  "intervalo_lectura_min": 10,
  "dispositivo_id": "sensor1"
}
```

**Response:** 200
```json
{
  "id": 1,
  "dispositivo_id": "sensor1",
  "intervalo_lectura_min": 10,
  ...
}
```

---

### 🌦️ CLIMA

#### GET /api/clima/pronostico
Obtener pronóstico meteorológico

**Query Parameters:**
- `ciudad` (string, default: "Mexico City")

**Response:** 200
```json
{
  "ciudad": "Mexico City",
  "clima_actual": {
    "temperatura": 28.5,
    "humedad": 65,
    "descripcion": "Nublado",
    "ciudad": "Mexico City"
  },
  "lluvia_pronostico": {
    "lluvia_total_mm": 2.5,
    "hay_lluvia": true,
    "horas_con_lluvia": 3,
    "intensidad_max": 1.2
  },
  "se_debe_regar": true,
  "umbral_lluvia_mm": 5.0,
  "horas_pronostico": 24,
  "actualizado": "2026-05-14T10:30:00Z"
}
```

---

#### GET /api/clima/actual
Obtener clima actual

**Query Parameters:**
- `ciudad` (string, default: "Mexico City")

**Response:** 200
```json
{
  "ciudad": "Mexico City",
  "temperatura": 28.5,
  "humedad_relativa": 65,
  "descripcion": "Nublado",
  "lluvia_hoy_mm": 0.5,
  "pronostico_lluvia_24h_mm": 2.5,
  "actualizado": "2026-05-14T10:30:00Z"
}
```

---

#### GET /api/clima/lluvia-24h
Lluvia esperada próximas 24 horas

**Query Parameters:**
- `ciudad` (string, default: "Mexico City")

**Response:** 200
```json
{
  "ciudad": "Mexico City",
  "lluvia_24h_mm": 2.5,
  "umbral_riego_mm": 5.0,
  "se_recomienda_riego": true,
  "consultado": "2026-05-14T10:30:00Z"
}
```

---

### 📊 DASHBOARD

#### GET /api/dashboard/actual
Dashboard en tiempo real

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "humedad_actual": 65.5,
  "temperatura_actual": 28.5,
  "riego_activo": true,
  "duracion_riego_restante": 250,
  "clima_ciudad": "Mexico City",
  "clima_temperatura": 28.5,
  "clima_lluvia_24h": 2.5,
  "umbral_humedad": 40,
  "ultimo_evento_riego": {...},
  "actualizado": "2026-05-14T10:30:00Z"
}
```

---

#### GET /api/dashboard/resumen
Resumen rápido del sistema

**Query Parameters:**
- `dispositivo_id` (string, default: "sensor1")

**Response:** 200
```json
{
  "dispositivo_id": "sensor1",
  "humedad": {
    "actual": 65.5,
    "promedio_1h": 63.45,
    "umbral": 40
  },
  "riego": {
    "activo": true,
    "ultimo_evento": "ON",
    "tiempo_total_hoy_min": 30.0
  },
  "actualizado": "2026-05-14T10:30:00Z"
}
```

---

### ℹ️ INFORMACIÓN

#### GET /
Información de la API

**Response:** 200
```json
{
  "nombre": "Sistema Riego Inteligente API",
  "version": "1.0.0",
  "descripcion": "API para control automático de riego basado en IoT",
  "documentacion": "/docs"
}
```

---

#### GET /health
Health check

**Response:** 200
```json
{
  "status": "OK",
  "servicio": "Sistema de Riego Inteligente"
}
```

---

## Códigos de Error

| Código | Significado |
|--------|------------|
| 200 | OK |
| 201 | Creado |
| 400 | Solicitud incorrecta |
| 404 | No encontrado |
| 503 | Servicio no disponible |

## Ejemplos con cURL

### Crear lectura
```bash
curl -X POST "http://localhost:8000/api/sensores/" \
  -H "Content-Type: application/json" \
  -d '{"humedad": 65.5, "dispositivo_id": "sensor1"}'
```

### Obtener estado
```bash
curl -X GET "http://localhost:8000/api/riego/estado"
```

### Activar riego
```bash
curl -X POST "http://localhost:8000/api/riego/forzar-on" \
  -H "Content-Type: application/json" \
  -d '{"accion": "ON", "duracion_segundos": 300}'
```

## Ejemplos con Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Crear lectura
response = requests.post(
    f"{BASE_URL}/api/sensores/",
    json={"humedad": 65.5, "dispositivo_id": "sensor1"}
)
print(response.json())

# Obtener estado
response = requests.get(f"{BASE_URL}/api/riego/estado")
print(response.json())

# Evaluar riego
response = requests.post(f"{BASE_URL}/api/riego/evaluar")
print(response.json())
```
