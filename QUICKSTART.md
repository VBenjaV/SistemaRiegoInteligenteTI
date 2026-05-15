# Guía de Inicio Rápido

## 🚀 Opción 1: Con Docker (Recomendado - Más Fácil)

### Requisitos
- Docker Desktop instalado
- API key de OpenWeatherMap (gratuita)

### Pasos

1. **Clonar/Abrir el proyecto**
```bash
cd c:\Users\benja\Desktop\InfraTIGrupo2\SistemaRiegoInteligenteTI
```

2. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp backend\.env.example backend\.env

# Editar backend\.env y agregar:
# - SUPABASE_DB_URL (connection string de Supabase)
# - WEATHER_API_KEY (OpenWeatherMap)
# Crear schema en Supabase SQL Editor con docs/supabase_schema.sql
```

3. **Levantar servicios**
```bash
docker-compose up -d
```

4. **Verificar que funciona**
```bash
# Backend
http://localhost:8000

# Documentación interactiva
http://localhost:8000/docs

# MQTT Broker
localhost:1883
```

---

## 🔧 Opción 2: Desarrollo Local (Más Control)

### Requisitos
- Python 3.11+
- Git (ya configurado)
- Mosquitto MQTT broker

### Pasos

1. **Instalar Mosquitto**

   **Windows:**
   - Descargar: https://mosquitto.org/download/
   - Instalar normalmente

   **Linux:**
   ```bash
   sudo apt-get install mosquitto mosquitto-clients
   ```

2. **Crear entorno virtual**
```bash
cd backend
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env y agregar:
# - SUPABASE_DB_URL (connection string de Supabase)
# - WEATHER_API_KEY (OpenWeatherMap)
```

5. **Iniciar Mosquitto MQTT**

   **Windows (CMD):**
   ```bash
   mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf"
   ```

   **Linux:**
   ```bash
   mosquitto
   ```

6. **Ejecutar backend**
```bash
python -m uvicorn main:app --reload
```

7. **Verificar**
   - Backend: http://localhost:8000
   - Docs: http://localhost:8000/docs

---

## 📝 Próximos Pasos

### 1. Enviar primer sensor
```bash
curl -X POST "http://localhost:8000/api/sensores/" \
  -H "Content-Type: application/json" \
  -d '{"humedad": 65.5, "dispositivo_id": "sensor1", "temperatura": 28.0}'
```

O usar simulador:
```bash
python backend/sensor_simulator.py --count 5 --interval 2
```

### 2. Ver dashboard
```bash
curl "http://localhost:8000/api/dashboard/actual"
```

### 3. Actualizar configuración
```bash
curl -X PUT "http://localhost:8000/api/config/umbral" \
  -H "Content-Type: application/json" \
  -d '{"umbral_humedad": 40, "dispositivo_id": "sensor1"}'
```

### 4. Activar riego manualmente
```bash
curl -X POST "http://localhost:8000/api/riego/forzar-on" \
  -H "Content-Type: application/json" \
  -d '{"accion": "ON", "duracion_segundos": 300, "dispositivo_id": "sensor1"}'
```

---

## 🔌 Conectar ESP32

1. Cargar firmware MicroPython (ver: `device/README.md`)
2. Copiar código de `device/esp32/main_example.py` al ESP32
3. Configurar WiFi y MQTT en el código
4. El ESP32 comenzará a publicar datos automáticamente

---

## 📊 Monitoreo

### Monitorear con MQTT

```bash
# Suscribirse a temas
mosquitto_sub -h localhost -t "jardin/#"

# O específicamente:
mosquitto_sub -h localhost -t "jardin/sensor1/humedad"
```

### Ver logs del backend

```bash
# Si corres con Docker
docker logs riego_backend

# Si corres localmente, ves los logs en la terminal
```

---

## 🧪 Tests

```bash
cd backend
pytest tests/
```

---

## 🛑 Parar servicios

**Con Docker:**
```bash
docker-compose down
```

**Local:**
- Ctrl+C en las terminales donde corren los servicios
- O: `mosquitto -k` (para Mosquitto)

---

## 📚 Documentación

- `ARCHITECTURE.md` - Arquitectura completa del sistema
- `README.md` - Descripción general
- `docs/API_REFERENCE.md` - Referencia detallada de endpoints
- `device/README.md` - Guía del firmware ESP32
- `backend/app/config.py` - Configuraciones disponibles

---

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Verificar que el puerto 8000 esté libre
netstat -ano | findstr :8000

# Si está en uso, cambiar en .env o matar el proceso
```

### MQTT no conecta
```bash
# Verificar que Mosquitto esté corriendo
netstat -ano | findstr :1883

# Reiniciar Mosquitto si es necesario
```

### Error de base de datos
```bash
# Verificar SUPABASE_DB_URL en backend/.env
# Revisar logs del backend
```

---

## 💡 Tips

1. **Documentación automática**: La API genera documentación interactiva en `/docs`
2. **Swagger UI**: Prueba todos los endpoints desde el navegador
3. **Logs detallados**: El backend registra todo lo que sucede
4. **Desarrollo rápido**: `--reload` recarga automáticamente al cambiar código

---

## 🎯 Próximas Fases

- [ ] Frontend Vue.js
- [ ] Autenticación de usuarios
- [ ] Notificaciones (email/SMS)
- [ ] Dashboard avanzado
- [ ] App móvil
- [ ] Análisis de datos
