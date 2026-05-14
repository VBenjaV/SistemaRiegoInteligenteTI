# Guía de Uso - Sistema de Riego Inteligente

## 🎯 Cómo Usar el Sistema Completo

### Parte 1: Backend (API REST + MQTT)

#### Paso 1: Iniciar el Backend

**Opción 1: Con Docker (RECOMENDADO)**
```bash
cd c:\Users\benja\Desktop\InfraTIGrupo2\SistemaRiegoInteligenteTI

# Copiar archivo .env
copy backend\.env.example backend\.env

# Editar backend\.env y agregar tu API key de OpenWeatherMap
# WEATHER_API_KEY=tu_clave_aqui

# Levantar servicios
docker-compose up -d

# Verificar
docker-compose ps
http://localhost:8000/docs
```

**Opción 2: Desarrollo Local**
```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
copy .env.example .env
# Editar .env con tu API key

# Iniciar Mosquitto (terminal separada)
mosquitto

# Ejecutar backend (otra terminal)
python -m uvicorn main:app --reload
```

#### Paso 2: Verificar que Backend Funciona

```bash
# Health check
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"OK","servicio":"Sistema de Riego Inteligente"}

# API Docs
http://localhost:8000/docs
```

---

### Parte 2: Frontend (Dashboard Vue.js)

#### Paso 1: Instalar y Ejecutar

```bash
cd frontend

# Instalar dependencias (primera vez)
npm install

# Ejecutar en desarrollo
npm run dev
```

#### Paso 2: Abrir en el Navegador

```
http://localhost:5173
```

**¡Deberías ver el Dashboard con 5 páginas!**

---

## 📊 Lo que Puedes Hacer en el Frontend

### 1. 📊 Dashboard (Página Principal)
- **Widget de Humedad**: Muestra porcentaje actual
- **Widget de Temperatura**: Temperatura del ambiente
- **Widget de Riego**: Estado ON/OFF
- **Widget de Clima**: Temperatura del clima
- **Control Principal**: Botones grandes para encender/apagar
- **Se actualiza automáticamente cada 30 segundos**

**Acciones:**
- Ajustar duración del riego (5, 10, 20 minutos o manual)
- Botón ENCENDER (verde)
- Botón APAGAR (rojo)

### 2. 📡 Sensores
- **Tabla de lecturas**: Histórico con todas las mediciones
- **Filtros**: Por rango de fechas o número de días
- **Estadísticas**: Promedio, mínimo, máximo
- **Descargar CSV**: Exportar datos a Excel

### 3. 💧 Control de Riego
- **Indicador grande**: Estado actual con animación
- **Controles**: Duración configurable
- **Historial**: Todos los eventos de riego
- **Estadísticas del día**: Tiempo total y ciclos

### 4. ⚙️ Configuración
- **Umbral de Humedad**: Valor para activar riego (%)
- **Intervalo de Lectura**: Cada cuántos minutos leer
- **Umbral de Lluvia**: mm de lluvia para no regar
- **Guardar Cambios**: Persiste en base de datos

### 5. 🌦️ Clima
- **Clima Actual**: Temperatura, humedad, descripción
- **Lluvia 24h**: mm esperados
- **Recomendación**: SI/NO regar basado en lluvia
- **Pronóstico 5 días**: Completo con temperaturas

---

## 🧪 Flujo Completo de Prueba

### Test 1: Crear una Lectura de Sensor

**Desde el Frontend:**
1. Abre DevTools (F12)
2. Console
3. Ejecuta:

```javascript
fetch('http://localhost:8000/api/sensores/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    humedad: 65.5,
    dispositivo_id: 'sensor1',
    temperatura: 28.0
  })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Resultado:** Deberías ver un objeto con id, humedad, timestamp, etc.

### Test 2: Ver en el Dashboard

1. Vuelve a la pestaña del Frontend
2. Recarga (F5) o espera 30 segundos
3. Los widgets deberían mostrar los datos

### Test 3: Activar Riego Manual

1. Ve a la página "💧 Riego"
2. Ajusta duración (por ejemplo: 300 segundos = 5 minutos)
3. Click en "🟢 ENCENDER"
4. Deberías ver el indicador en verde
5. Mira el "Historial de Eventos" - verás el evento registrado

### Test 4: Configurar Umbral

1. Ve a "⚙️ Configuración"
2. Cambia "Umbral de Humedad" a 50
3. Click "💾 Guardar Cambios"
4. Verás mensaje ✅
5. En el Backend se actualiza la BD

---

## 🔄 Flujo Completo de Datos

```
1. ESP32 (simulado o real)
   ↓ MQTT Publish
   "jardin/sensor1/humedad" → {"humedad": 65.5}
   ↓
2. MQTT Broker (Mosquitto)
   ↓
3. Backend FastAPI
   ├─ Recibe datos
   ├─ Guarda en BD
   ├─ Consulta OpenWeatherMap API
   ├─ Ejecuta lógica de riego
   ├─ Publica comando MQTT si necesario
   ↓
4. API REST (20 endpoints)
   ↓
5. Frontend Vue.js
   ├─ GET /api/sensores/actual        → Dashboard, Sensores
   ├─ GET /api/riego/estado           → Control de Riego
   ├─ GET /api/clima/pronostico       → Página Clima
   ├─ GET /api/config/                → Configuración
   ├─ POST /api/riego/forzar-on       → Control manual
   └─ ...muchos más
   ↓
6. Dashboard actualizado
   ├─ Widgets en tiempo real
   ├─ Históricos
   ├─ Control interactivo
   └─ Información meteorológica
```

---

## 📱 Navegación en el Frontend

**Barra de Navegación (arriba)**
```
🌾 Riego Inteligente | 📊 Dashboard | 📡 Sensores | 💧 Riego | 🌦️ Clima | ⚙️ Config
```

- Click en cualquier ícono para cambiar de página
- La página activa aparece en azul

---

## ✅ Checklist Final

### Backend
- [ ] `docker-compose ps` muestra 2 servicios UP (o Mosquitto + Uvicorn corriendo)
- [ ] `http://localhost:8000/health` retorna OK
- [ ] `http://localhost:8000/docs` muestra Swagger UI

### Frontend
- [ ] `npm run dev` ejecuta sin errores
- [ ] `http://localhost:5173` abre el Dashboard
- [ ] Los 5 menúes están visibles arriba
- [ ] Los widgets muestran "-" (sin datos iniciales es normal)

### Integración
- [ ] Puedes crear lecturas desde Frontend
- [ ] Los datos aparecen en el Dashboard
- [ ] Puedes encender/apagar riego
- [ ] Puedes cambiar configuración

---

## 🐛 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Frontend no carga | Verificar `http://localhost:5173` está accesible |
| "Cannot reach backend" | Backend en puerto 8000 debe estar corriendo |
| Datos no aparecen | Crear lectura primero desde API o CLI |
| Estilos rotos | `npm run build`, luego `npm run preview` |
| MQTT no conecta | Verificar Mosquitto corriendo en puerto 1883 |
| Base de datos vacía | Normal - necesita lecturas para mostrar datos |

---

## 🎉 ¡Listo!

Tienes un sistema completo de:
- ✅ Backend API REST con 20 endpoints
- ✅ MQTT para comunicación IoT
- ✅ Base de datos con histórico
- ✅ Frontend Dashboard interactivo
- ✅ Integración meteorológica
- ✅ Lógica de riego inteligente

**¡Disfruta controlando tu sistema de riego!** 🌾

---

## 📚 Documentación Adicional

- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica completa
- [backend/README.md](backend/README.md) - Detalles del backend
- [frontend/README.md](frontend/README.md) - Detalles del frontend
- [backend/app/config.py](backend/app/config.py) - Variables de entorno
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - Todos los endpoints

---

¿Preguntas? Revisa cualquiera de estos archivos o prueba los endpoints en `http://localhost:8000/docs` 🚀
