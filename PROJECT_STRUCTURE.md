# Estructura del Proyecto - Resumen Ejecutivo

## 📁 Árbol de Directorios Completo

```
SistemaRiegoInteligenteTI/
│
├── 📄 README.md                    # Descripción general del proyecto
├── 📄 QUICKSTART.md               # Guía de inicio rápido
├── 📄 ARCHITECTURE.md             # Documentación de arquitectura detallada
├── 📄 docker-compose.yml          # Orquestación de servicios
├── 📄 .gitignore                  # Archivos a ignorar en git
│
├── backend/                        # Backend FastAPI
│   ├── 📄 requirements.txt         # Dependencias Python
│   ├── 📄 .env.example            # Variables de entorno (ejemplo)
│   ├── 📄 main.py                 # Punto de entrada de la aplicación
│   ├── 📄 client_example.py       # Cliente Python para pruebas
│   ├── 📄 sensor_simulator.py     # Simulador de sensor (API)
│   ├── 📄 Dockerfile             # Contenedor Docker
│   │
│   ├── app/                        # Paquete principal
│   │   ├── __init__.py
│   │   ├── 📄 config.py           # Configuración y variables
│   │   │
│   │   ├── models/                # Modelos de datos Pydantic
│   │   │   ├── __init__.py
│   │   │   └── 📄 schemas.py      # Esquemas de validación
│   │   │
│   │   ├── db/                    # Base de datos SQLAlchemy
│   │   │   ├── __init__.py
│   │   │   └── 📄 database.py     # Modelos ORM y conexión
│   │   │
│   │   ├── services/              # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   ├── 📄 mqtt_service.py          # Cliente MQTT
│   │   │   ├── 📄 weather_service.py       # API meteorológica
│   │   │   ├── 📄 database_service.py      # CRUD operations
│   │   │   └── 📄 irrigation_logic.py      # Lógica de riego
│   │   │
│   │   └── api/                   # Endpoints REST
│   │       ├── __init__.py
│   │       ├── 📄 sensores.py     # GET/POST lecturas
│   │       ├── 📄 riego.py        # Control de riego
│   │       ├── 📄 configuracion.py # Config del sistema
│   │       ├── 📄 clima.py        # Datos meteorológicos
│   │       └── 📄 dashboard.py    # Dashboard en tiempo real
│   │
│   └── tests/                      # Tests unitarios
│       └── 📄 test_api.py         # Tests de endpoints
│
├── device/                         # Código para dispositivos
│   ├── 📄 README.md              # Guía de instalación del firmware
│   └── esp32/                      # Código ESP32
│       └── 📄 main_example.py    # Firmware MicroPython (ejemplo)
│
├── frontend/                       # Frontend (próximamente)
│   └── 📄 README.md              # Instrucciones de desarrollo
│
├── mosquitto/                      # Configuración MQTT
│   └── config/
│       └── 📄 mosquitto.conf     # Configuración del broker
│
└── docs/                           # Documentación adicional
    └── 📄 API_REFERENCE.md        # Referencia detallada de API
```

## 📊 Componentes Principales

### Backend FastAPI
**Ubicación:** `backend/app/`

| Módulo | Responsabilidad | Archivos |
|--------|-----------------|----------|
| **Models** | Esquemas de validación | `models/schemas.py` |
| **DB** | Base de datos y ORM | `db/database.py` |
| **Services** | Lógica de negocio | `services/*.py` |
| **API** | Endpoints REST | `api/*.py` |

### Servicios
**Ubicación:** `backend/app/services/`

1. **mqtt_service.py** (266 líneas)
   - Cliente MQTT
   - Publicación y suscripción
   - Manejo de conexiones

2. **weather_service.py** (208 líneas)
   - Integración OpenWeatherMap
   - Pronóstico de lluvia
   - Lógica meteorológica

3. **database_service.py** (268 líneas)
   - CRUD para sensores
   - CRUD para eventos de riego
   - CRUD para configuración
   - Gestión de clima

4. **irrigation_logic.py** (218 líneas)
   - Lógica de decisión de riego
   - Evaluación de condiciones
   - Control automático y manual

### API Endpoints
**Ubicación:** `backend/app/api/`

| Módulo | Endpoints | Cantidad |
|--------|-----------|----------|
| `sensores.py` | GET/POST lecturas | 4 |
| `riego.py` | Control de riego | 6 |
| `configuracion.py` | Config del sistema | 4 |
| `clima.py` | Datos meteorológicos | 4 |
| `dashboard.py` | Dashboard | 2 |
| **Total** | | **20 endpoints** |

## 🔄 Flujo de Datos

```
ESP32 → MQTT Broker → Backend FastAPI
                          ↓
                    Weather API (OpenWeatherMap)
                          ↓
                    Lógica de Riego Inteligente
                          ↓
                    Base de Datos Supabase (PostgreSQL)
                          ↓
                    API REST → Frontend (próximamente)
```

## 📦 Dependencias Principales

```
fastapi==0.104.1          # Framework web
paho-mqtt==1.6.1          # Cliente MQTT
sqlalchemy==2.0.23        # ORM para base de datos
requests==2.31.0          # Cliente HTTP (para APIs)
pydantic==2.5.0           # Validación de datos
python-dotenv==1.0.0      # Gestión de variables de entorno
```

## 🚀 Flujo de Inicio

```
1. docker-compose up
   │
   ├─→ Mosquitto inicia en puerto 1883
   ├─→ Supabase Postgres se inicializa
   └─→ Backend FastAPI inicia en puerto 8000
       │
       ├─→ init_db() crea tablas
       ├─→ init_mqtt() conecta a broker
       └─→ Aplicación lista en /docs

2. ESP32 conecta
   │
   ├─→ Conecta WiFi
   ├─→ Conecta MQTT
   └─→ Comienza a publicar sensores cada 5 minutos

3. Backend procesa
   │
   ├─→ Recibe datos de sensor
   ├─→ Guarda en BD
   ├─→ Consulta pronóstico cada hora
   ├─→ Evalúa lógica de riego
   └─→ Publica comandos a ESP32
```

## 🔐 Seguridad (Implementado)

- ✅ Validación de datos con Pydantic
- ✅ Tipado estricto
- ✅ Manejo de excepciones
- ✅ Logging de todas las operaciones
- ✅ CORS configurado

## 🔐 Seguridad (Por Implementar)

- ⏳ Autenticación JWT
- ⏳ Rate limiting
- ⏳ HTTPS/TLS
- ⏳ MQTT autenticado

## 📊 Base de Datos

### Tablas

```sql
CREATE TABLE ciudades (
   id INT PRIMARY KEY,
   nombre VARCHAR(100),
   codigo_pais VARCHAR(5)
);

CREATE TABLE dispositivos (
   id VARCHAR(50) PRIMARY KEY,
   nombre VARCHAR(100),
   ciudad_id INT,
   ubicacion_detallada VARCHAR(200),
   activo BOOLEAN
);

CREATE TABLE lecturas_sensores (
   id BIGINT PRIMARY KEY,
   dispositivo_id VARCHAR(50),
   humedad FLOAT,
   temperatura FLOAT,
   fecha_lectura DATETIME,
   creado DATETIME
);

CREATE TABLE eventos_riego (
    id INT PRIMARY KEY,
    dispositivo_id VARCHAR(50),
    accion VARCHAR(10),  -- ON/OFF
    duracion_segundos INT,
    manual BOOLEAN,
    timestamp DATETIME,
    creado DATETIME
);

CREATE TABLE configuracion (
   dispositivo_id VARCHAR(50) PRIMARY KEY,
   umbral_humedad INT,
   intervalo_lectura_min INT,
   lluvia_minima_mm FLOAT,
   horas_pronostico INT,
   actualizado DATETIME,
   creado DATETIME
);

CREATE TABLE pronostico_clima (
   id INT PRIMARY KEY,
   ciudad_id INT,
   fecha_pronostico DATETIME,
   lluvia_esperada_mm FLOAT,
   temperatura_max FLOAT,
   temperatura_min FLOAT,
   humedad_relativa INT,
   descripcion VARCHAR(200),
   actualizado DATETIME
);
```

## 📝 Configuración por Archivo

### `.env`
```
DEBUG=True
SUPABASE_DB_URL=postgresql+psycopg2://user:pass@host:5432/dbname
MQTT_BROKER_HOST=localhost
WEATHER_API_KEY=your_key
```

### `mosquitto.conf`
```
listener 1883 protocol mqtt
listener 9001 protocol websockets
allow_anonymous true
```

### `requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
paho-mqtt==1.6.1
...
```

## 🧪 Testing

```bash
# Ubicación: backend/tests/
# Ejecutar: pytest tests/

# Coverage:
# - Health checks
# - Endpoints de sensores
# - Control de riego
# - Configuración
# - Dashboard
```

## 📈 Escalabilidad

**Actual (Single Device):**
- 1 dispositivo por instalación
- 1 broker MQTT
- 1 backend FastAPI
- Supabase Postgres (nube)

**Futuro (Multi Device):**
- N dispositivos con IDs únicos
- Broker MQTT escalable (HiveMQ Cloud)
- Backend en Kubernetes
- Supabase Postgres (nube)
- Caché con Redis

## 🔄 Ciclo de Desarrollo

1. **Nuevo Feature**
   - Crear modelo en `models/schemas.py`
   - Crear servicio en `services/`
   - Crear endpoint en `api/`
   - Incluir en `api/__init__.py`
   - Agregar tests

2. **Testing**
   - Tests unitarios en `tests/`
   - Probar con `client_example.py`
   - Verificar en `/docs`

3. **Deployment**
   - Build: `docker build -t riego-backend backend/`
   - Run: `docker run ...`
   - Or: `docker-compose up`

## 📚 Documentación Generada

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 💾 Almacenamiento de Datos

- **Desarrollo**: Supabase Postgres (nube)
- **Producción**: Supabase Postgres (nube)
- **Caché**: Redis (próximo)
- **Archivos**: Ninguno (todo en BD)

## 🎯 Roadmap

**Fase 1 (Actual):** ✅ Completa
- Backend API completo
- MQTT broker
- Base de datos
- Lógica de riego

**Fase 2:** En desarrollo
- Frontend Vue.js
- Autenticación de usuarios
- Dashboard mejorado

**Fase 3:** Planificado
- App móvil
- Notificaciones
- Análisis de datos

## 📞 Soporte

- Documentación: `ARCHITECTURE.md`
- API Docs: `docs/API_REFERENCE.md`
- Inicio rápido: `QUICKSTART.md`
- Issues: Revisar logs en terminal
