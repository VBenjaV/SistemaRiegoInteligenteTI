# Sistema de Riego Inteligente con IoT

Diseño e implementación completa de un sistema de automatización de riego basado en IoT, utilizando:

- **Backend**: FastAPI + Python
- **Dispositivo Edge**: ESP32 con MQTT
- **Comunicación**: MQTT Broker (Mosquitto)
- **Base de Datos**: Supabase (PostgreSQL)
- **Frontend**: Vue.js (próximamente)
- **Integración Meteorológica**: OpenWeatherMap API

## 🎯 Características

- ✅ Lectura automática de sensores de humedad
- ✅ Lógica inteligente de riego basada en clima
- ✅ Comunicación en tiempo real vía MQTT
- ✅ Dashboard API REST completa
- ✅ Control manual y automático
- ✅ Histórico de eventos y datos
- ✅ Configuración personalizable

## 📁 Estructura del Proyecto

```
SistemaRiegoInteligenteTI/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/               # Endpoints REST
│   │   ├── models/            # Modelos Pydantic
│   │   ├── services/          # Lógica de negocio
│   │   ├── db/                # Base de datos
│   │   └── config.py          # Configuración
│   ├── tests/                 # Tests
│   ├── requirements.txt       # Dependencias Python
│   ├── main.py               # Punto de entrada
│   └── Dockerfile            # Contenedor Docker
├── device/                    # Código para ESP32
│   └── esp32/                # Firmware MicroPython
├── frontend/                  # Frontend Vue.js
├── docs/                      # Documentación
├── docker-compose.yml        # Orquestación de contenedores
├── mosquitto/                # Configuración MQTT
├── ARCHITECTURE.md           # Documentación de arquitectura
└── README.md                 # Este archivo
```

## 🚀 Inicio Rápido

### Opción 1: Con Docker Compose (Recomendado)

```bash
# Clonar el repositorio
git clone <repo>
cd SistemaRiegoInteligenteTI

# Crear archivo .env
cp backend/.env.example backend/.env
# Editar backend/.env y agregar:
# - SUPABASE_DB_URL (connection string de Supabase)
# - WEATHER_API_KEY (OpenWeatherMap)
# Crear schema en Supabase SQL Editor con docs/supabase_schema.sql

# Ejecutar con Docker Compose
docker-compose up -d
```

Backend estará disponible en: `http://localhost:8000`

### Opción 2: Desarrollo Local

```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Crear archivo .env
cp backend/.env.example backend/.env
# Editar backend/.env y agregar:
# - SUPABASE_DB_URL (connection string de Supabase)
# - WEATHER_API_KEY (OpenWeatherMap)

# Iniciar Mosquitto MQTT (en terminal separada)
# En Windows: descargar Eclipse Mosquitto
# En Linux: sudo apt-get install mosquitto && mosquitto

# Ejecutar backend
cd backend
python -m uvicorn main:app --reload
```

## 📚 API Endpoints

### Sensores
- `POST /api/sensores/` - Crear lectura
- `GET /api/sensores/actual` - Última lectura
- `GET /api/sensores/historial` - Historial
- `GET /api/sensores/promedio` - Promedio de humedad

### Riego
- `GET /api/riego/estado` - Estado actual
- `POST /api/riego/evaluar` - Ejecutar lógica de riego
- `POST /api/riego/forzar-on` - Activar manualmente
- `POST /api/riego/forzar-off` - Desactivar manualmente
- `GET /api/riego/historial` - Historial de eventos
- `GET /api/riego/tiempo-total-hoy` - Tiempo de riego hoy

### Configuración
- `GET /api/config/` - Obtener configuración
- `PUT /api/config/umbral` - Actualizar umbral de humedad
- `PUT /api/config/intervalo` - Actualizar intervalo de lectura

### Clima
- `GET /api/clima/pronostico` - Pronóstico meteorológico
- `GET /api/clima/actual` - Clima actual
- `GET /api/clima/lluvia-24h` - Lluvia esperada 24h
- `POST /api/clima/actualizar-pronostico` - Actualizar BD

### Dashboard
- `GET /api/dashboard/actual` - Dashboard en tiempo real
- `GET /api/dashboard/resumen` - Resumen rápido

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# API
DEBUG=True
API_TITLE=Sistema Riego Inteligente API
API_VERSION=1.0.0

# Supabase
SUPABASE_DB_URL=postgresql+psycopg2://user:pass@host:5432/dbname
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC_SUBSCRIBE_HUMIDITY=jardin/sensor1/humedad
MQTT_TOPIC_PUBLISH_COMMAND=jardin/bomba/comando

# Weather API
WEATHER_API_KEY=your_key_here
WEATHER_CITY=Mexico City
WEATHER_RAIN_THRESHOLD_MM=5

# Riego
HUMIDITY_THRESHOLD_PERCENT=40
IRRIGATION_DURATION_SECONDS=300
```

## 🤖 Lógica de Riego Inteligente

```python
CADA 5 MINUTOS:
  1. Leer humedad del sensor
  2. SI humedad < umbral (40%):
       a. Consultar pronóstico de lluvia
       b. SI lluvia < 5mm:
            - Activar riego 5 minutos
       c. SI lluvia >= 5mm:
            - No activar (lluvia próxima)
  3. SI riego activo y expiró:
       - Desactivar
```

## 📊 Base de Datos

Schema en Supabase: ver docs/supabase_schema.sql.

### Tablas principales

**ciudades**
- id, nombre, codigo_pais

**dispositivos**
- id, nombre, ciudad_id, ubicacion_detallada, activo

**lecturas_sensores**
- id, dispositivo_id, humedad, temperatura, fecha_lectura

**eventos_riego**
- id, dispositivo_id, accion (ON/OFF), duracion, manual, timestamp

**configuracion**
- id, dispositivo_id, umbral_humedad, intervalo_lectura

**pronostico_clima**
- id, ciudad_id, fecha_pronostico, lluvia_mm, temperatura, humedad

## 🔌 Temas MQTT

### Publicación (Device → Backend)
```
jardin/sensor1/humedad        → {"humedad": 65, "timestamp": "..."}
jardin/sensor1/temperatura    → {"temperatura": 28.5, "timestamp": "..."}
```

### Suscripción (Backend → Device)
```
jardin/bomba/comando          → {"accion": "ON", "duracion_segundos": 300}
```

## 🧪 Testing

```bash
cd backend
pytest tests/
```

Simular sensor:
```bash
python backend/sensor_simulator.py --count 5 --interval 2
```

## 📱 Frontend (Próximamente)

Aplicación Vue.js con:
- Dashboard en tiempo real
- Gráficos históricos
- Control manual
- Panel de configuración

## ☁️ Despliegue en AWS EC2

Guía paso a paso (Docker Compose en producción): **[docs/DEPLOY_EC2.md](./docs/DEPLOY_EC2.md)**

```bash
# En el servidor EC2
bash scripts/ec2-setup.sh
./scripts/deploy-prod.sh
```

## 🐳 Docker

### Build
```bash
docker build -t riego-backend backend/
```

### Run
```bash
docker run -p 8000:8000 \
     -e SUPABASE_DB_URL=postgresql+psycopg2://... \
  -e MQTT_BROKER_HOST=localhost \
  -e WEATHER_API_KEY=your_key \
  riego-backend
```

## 📖 Documentación Completa

Ver [ARCHITECTURE.md](./ARCHITECTURE.md) para documentación detallada de:
- Arquitectura del sistema
- Flujos de datos
- Algoritmos de decisión
- Seguridad
- Escalabilidad

## 🛠️ Desarrollo

### Agregar nueva funcionalidad

1. **Crear modelo** en `app/models/schemas.py`
2. **Crear servicio** en `app/services/`
3. **Crear endpoint** en `app/api/`
4. **Incluir en router** en `app/api/__init__.py`

### Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error")
```

## 🔒 Seguridad (Próxima Fase)

- [ ] Autenticación JWT para API
- [ ] TLS/SSL para MQTT
- [ ] Validación de datos mejorada
- [ ] Rate limiting
- [ ] Sanitización de inputs

## 📈 Próximas Mejoras

- [ ] Dashboard Vue.js
- [ ] Autenticación de usuarios
- [ ] Notificaciones (email/SMS)
- [ ] Análisis de datos avanzado
- [ ] Soporte multi-dispositivo mejorado
- [ ] App móvil
- [ ] Predicciones con ML

## 📝 Licencia

MIT

## 👨‍💻 Autor

Grupo 2 - Sistema de Riego Inteligente

## 📧 Contacto

Para preguntas o sugerencias, contactar al equipo de desarrollo.

## 🙏 Agradecimientos

- FastAPI por el framework excelente
- Mosquitto por el broker MQTT
- OpenWeatherMap por los datos meteorológicos
- La comunidad de Python
