# Arquitectura del Sistema de Riego Inteligente

## Descripción General

Sistema de IoT para automatización del riego agrícola/residencial con microcontrolador ESP32 que se comunica con un backend FastAPI mediante MQTT, permitiendo toma de decisiones inteligente basada en humedad del suelo y datos meteorológicos.

## Capas del Sistema

### 1. Capa de Dispositivo (Edge) - ESP32

**Componentes:**
- Microcontrolador: ESP32 (Wi-Fi integrado)
- Sensores: Sensor de humedad del suelo (analógico/digital)
- Actuadores: Electroválvula o bomba de agua
- Conexión: Wi-Fi para MQTT

**Responsabilidades:**
- Lectura periódica de sensores (cada 5-10 minutos)
- Gestión de conexión Wi-Fi y reconexión automática
- Publicación de datos en MQTT: `jardin/sensor1/humedad`
- Suscripción a comandos MQTT: `jardin/bomba/comando`
- Actuación local (encendido/apagado de válvula)
- Logs locales de eventos

**Flujo de Datos:**
```
Sensor → ESP32 → MQTT Publish → Backend
Backend → MQTT Publish → ESP32 → Actuador (Válvula)
```

### 2. Capa de Comunicación - MQTT

**Broker MQTT:**
- Mosquitto (local) o HiveMQ / AWS IoT Core (nube)
- Puerto: 1883 (no seguro) o 8883 (seguro)

**Temas (Topics):**

#### Publicación del Dispositivo (Device → Backend):
```
jardin/sensor1/humedad        → {"humedad": 65, "timestamp": "2026-05-14T10:30:00Z"}
jardin/sensor1/temperatura    → {"temperatura": 28.5, "timestamp": "..."}
jardin/dispositivo/estado     → {"conectado": true, "bateria": 85}
```

#### Comandos del Backend (Backend → Device):
```
jardin/bomba/comando          → {"accion": "ON", "duracion_segundos": 300}
jardin/config/umbral          → {"umbral": 40}
```

**Formato de Mensajes:**
- Todos los mensajes en JSON
- Incluir timestamp en ISO 8601
- Incluir identificador del sensor/dispositivo

### 3. Capa de Backend - FastAPI

**Responsabilidades Principales:**

#### 3.1 Gestión MQTT
- Cliente MQTT que se suscribe a temas de sensores
- Publicación de comandos de control
- Manejo de reconexión automática
- Logging de eventos

#### 3.2 Lógica de Riego Inteligente
```python
SI humedad < umbral (40%)
   Y pronóstico_lluvia_24h < 5mm
ENTONCES
   publicar comando MQTT: {"accion": "ON", "duracion": 300}
   registrar evento en BD
FIN SI
```

#### 3.3 Integración Meteorológica
- Consultar API OpenWeatherMap cada hora
- Obtener: pronóstico de lluvia, humedad ambiental, temperatura
- Usar en decisiones de riego

#### 3.4 Base de Datos
- Almacenar: lecturas de humedad, eventos de riego, configuración
- Histórico completo para análisis

#### 3.5 API REST - Endpoints

```
GET    /api/sensores/actual           → Última lectura del sensor
GET    /api/sensores/historial        → Histórico (filtrable por fecha)
GET    /api/riego/estado              → Estado actual del riego
GET    /api/riego/historial           → Logs de ciclos de riego
GET    /api/clima/pronostico          → Pronóstico meteorológico
GET    /api/config                    → Configuración actual
POST   /api/riego/forzar-on           → Encender riego manual
POST   /api/riego/forzar-off          → Apagar riego manual
PUT    /api/config/umbral             → Actualizar umbral de humedad
PUT    /api/config/intervalo          → Actualizar intervalo de muestreo
GET    /docs                          → Swagger UI (autogenerado)
```

### 4. Capa de Persistencia - Base de Datos

**Tecnología:** Supabase (PostgreSQL)

**Tablas Principales:**

#### ciudades
```sql
id, nombre, codigo_pais
```

#### dispositivos
```sql
id, nombre, ciudad_id, ubicacion_detallada, activo
```

#### lecturas_sensores
```sql
id, dispositivo_id, humedad, temperatura, fecha_lectura, creado
```

#### eventos_riego
```sql
id, dispositivo_id, accion (ON/OFF), duracion_segundos, manual, timestamp
```

#### configuracion
```sql
dispositivo_id, umbral_humedad, intervalo_lectura_min,
lluvia_minima_mm, horas_pronostico, actualizado, creado
```

#### pronostico_clima
```sql
id, ciudad_id, fecha_pronostico, lluvia_esperada_mm, temperatura_max,
humedad_relativa, actualizado
```

### 5. Capa de Interfaz de Usuario - Frontend

**Tecnología:** Vue.js (o framework similar)

**Funcionalidades:**
- Dashboard en tiempo real
- Gráficos históricos de humedad
- Información meteorológica
- Control manual de riego
- Panel de configuración (umbrales, intervalos)
- Logs de eventos

## Flujo Integral de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    DISPOSITIVO ESP32                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Sensor Humedad → ADC → procesamiento → caché local  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬────────────────────────────────────────────────┘
             │ Publish: {"humedad": 65}
             ▼
    ┌──────────────────┐
    │  MQTT Broker     │
    │  (Mosquitto)     │
    └──────────────────┘
             │ Subscribe
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND FastAPI                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MQTT Service: Recibe datos → valida → almacena      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Weather Service: Consulta API cada hora              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Irrigation Logic: Evalúa condiciones → publica cmd  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ REST API: Endpoints para UI y control manual         │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬───────────────────────────────┬─────────────────┘
             │ Publish: {"accion": "ON"}     │ Respuesta JSON
             │                               │
             ▼                               ▼
     ┌──────────────┐              ┌─────────────────────┐
     │ ESP32 recibe │              │  Web UI (Vue.js)    │
     │ y ejecuta    │              │  - Dashboard        │
     │ comando      │              │  - Gráficos         │
     └──────────────┘              │  - Control          │
                                   └─────────────────────┘
```

## Algoritmo de Toma de Decisión

```
CADA 5 MINUTOS:
  1. Leer última humedad del sensor
  2. SI humedad < umbral_configurado:
       a. Consultar pronóstico de lluvia (próximas 24h)
       b. SI lluvia_esperada < 5mm:
            - Publicar comando MQTT: ON
            - Establecer timer de duración (ej: 5 min)
            - Registrar evento en BD
          SINO:
            - No activar riego (lluvia próxima)
  3. SI riego estaba activo:
       a. Verificar si expiró duración
       b. Si expiró: publicar comando MQTT: OFF

CADA 1 HORA:
  - Actualizar pronóstico meteorológico
```

## Seguridad

- MQTT con autenticación usuario/contraseña (opcional: TLS/SSL)
- API REST sin autenticación (usar JWT/OAuth en producción)
- Validación Pydantic en todos los endpoints
- Rate limiting (futuro)
- HTTPS en producción

## Escalabilidad

- Diseño multi-dispositivo: cada ESP32 tiene ID único
- Topics MQTT escalables: `jardin/{dispositivo_id}/humedad`
- BD relacional permite múltiples usuarios/jardines
- API preparada para múltiples clientes simultáneos

## Tecnologías Stack

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Device | ESP32 + MicroPython | Bajo costo, Wi-Fi integrado, comunidad |
| Comunicación | MQTT | Protocolo IoT estándar, bajo overhead |
| Backend | FastAPI + Python | Desarrollo rápido, documentación automática |
| BD | Supabase (PostgreSQL) | Relacional, fiable, escalable |
| Frontend | Vue.js | Reactivo, ecosistema robusto |
| Clima | OpenWeatherMap API | Gratuita, confiable, completa |

## Deployment

### Desarrollo
- Backend: `uvicorn main:app --reload`
- MQTT: Mosquitto en localhost:1883
- BD: Supabase Postgres (nube)

### Producción
- Backend: Gunicorn + Nginx en servidor
- MQTT: HiveMQ Cloud o AWS IoT Core
- BD: Supabase Postgres
- Frontend: Vercel / Netlify

## Próximas Fases

1. Implementación de autenticación de usuarios
2. Dashboard mejorado con más métricas
3. Notificaciones (email/SMS)
4. Análisis de datos y recomendaciones
5. Soporte para múltiples zonas de riego
