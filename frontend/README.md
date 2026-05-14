# Frontend - Sistema de Riego Inteligente

Dashboard web completo para control y monitoreo del sistema de riego inteligente.

## 🚀 Inicio Rápido

### Requisitos
- Node.js 18+ (descargar de https://nodejs.org/)
- npm (incluido con Node.js)

### Instalación

```bash
# Entrar a carpeta del frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

Abre el navegador en `http://localhost:5173`

### Build para producción

```bash
npm run build
npm run preview
```

---

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/       # Componentes reutilizables
│   │   ├── NavBar.vue
│   │   ├── WidgetHumedad.vue
│   │   ├── WidgetTemperatura.vue
│   │   ├── WidgetRiego.vue
│   │   └── WidgetClima.vue
│   │
│   ├── views/            # Páginas principales
│   │   ├── DashboardView.vue
│   │   ├── SensoresView.vue
│   │   ├── ControlRiegoView.vue
│   │   ├── ConfiguracionView.vue
│   │   └── ClimaView.vue
│   │
│   ├── stores/           # Pinia stores (estado global)
│   │   ├── dashboard.ts
│   │   ├── sensores.ts
│   │   ├── riego.ts
│   │   ├── config.ts
│   │   └── clima.ts
│   │
│   ├── services/         # API client
│   │   └── api.ts        # Configuración de Axios
│   │
│   ├── router/           # Rutas
│   │   └── index.ts
│   │
│   ├── App.vue           # Componente raíz
│   ├── main.ts           # Punto de entrada
│   └── style.css         # Estilos globales
│
├── public/               # Archivos estáticos
├── package.json          # Dependencias
├── vite.config.ts        # Configuración Vite
├── tailwind.config.js    # Configuración Tailwind CSS
└── index.html            # HTML principal
```

---

## 🎨 Páginas Disponibles

### 📊 Dashboard
- Resumen en tiempo real
- Widgets de estado (humedad, temperatura, riego, clima)
- Control principal de riego
- Botones ON/OFF grandes
- Actualización automática cada 30 segundos

### 📡 Sensores
- Tabla histórica de lecturas
- Filtros por rango de fechas
- Estadísticas (promedio, mín, máx)
- Descargar datos en CSV
- Gráfico de tendencias

### 💧 Control de Riego
- Indicador grande de estado
- Botones ON/OFF grandes
- Duración configurable
- Historial de eventos
- Estadísticas del día

### ⚙️ Configuración
- Umbral de humedad
- Intervalo de lectura
- Umbral de lluvia
- Horas de pronóstico
- Guardar cambios

### 🌦️ Clima
- Clima actual
- Lluvia esperada 24h
- Recomendación de riego
- Pronóstico 5 días
- Información meteorológica

---

## 🔧 Tecnologías

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Vue.js | 3.3+ | Framework web |
| TypeScript | 5.2+ | Tipado estático |
| Pinia | 2.1+ | Gestión de estado |
| Axios | 1.5+ | Cliente HTTP |
| Tailwind CSS | 3.3+ | Estilos |
| Vite | 5.0+ | Build tool |

---

## 🎯 Features

✅ **Dashboard en tiempo real**
- Actualización automática cada 30 segundos
- Widgets de estado rápido
- Control de riego desde el dashboard

✅ **Gestión de datos**
- Histórico de sensores con filtros
- Estadísticas calculadas
- Exportación a CSV

✅ **Control intuitivo**
- Botones grandes y claros
- Indicadores visuales
- Confirmación de acciones

✅ **Información meteorológica**
- Pronóstico 5 días
- Recomendaciones de riego
- Integración con API de OpenWeatherMap

✅ **Configuración flexible**
- Umbral de humedad ajustable
- Intervalo de lectura personalizable
- Guardar cambios en BD

---

## 🔄 Flujo de Datos

```
UI (Vue) → Axios → Backend FastAPI (http://localhost:8000)
    ↓
Pinia Stores (Estado Global)
    ↓
Components (Reactivos)
```

---

## 🚨 Troubleshooting

### "Cannot connect to http://localhost:8000"
- Verificar que el backend está corriendo: `http://localhost:8000/health`
- Verificar CORS está habilitado en backend
- Revisar puerto en vite.config.ts

### "npm install" falla
```bash
# Limpiar cache de npm
npm cache clean --force

# Instalar de nuevo
npm install
```

### El puerto 5173 ya está en uso
```bash
# Usar otro puerto
npm run dev -- --port 5174
```

### Los estilos no se cargan
```bash
# Rebuildar Tailwind CSS
npm run build
```

---

## 📱 Responsive Design

- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Mobile (320px - 767px)

Usa `md:` y `lg:` de Tailwind CSS para breakpoints.

---

## 🔐 Seguridad (Próxima Fase)

- [ ] Autenticación JWT
- [ ] Validación de tokens
- [ ] Protección de rutas
- [ ] Encriptación de datos sensibles

---

## 📊 Scripts disponibles

| Script | Función |
|--------|---------|
| `npm run dev` | Iniciar servidor de desarrollo |
| `npm run build` | Build para producción |
| `npm run preview` | Preview de producción |
| `npm run lint` | Linter de código |

---

## 🎓 Desarrollo

### Agregar un nuevo componente

1. Crear archivo en `src/components/MiComponente.vue`
2. Importar en la vista donde se use
3. Usar en el template

```vue
<script setup lang="ts">
import MiComponente from '@/components/MiComponente.vue'
</script>

<template>
  <MiComponente />
</template>
```

### Agregar una nueva página

1. Crear archivo en `src/views/MiVista.vue`
2. Importar en `src/router/index.ts`
3. Agregar ruta

```ts
{
  path: '/mi-ruta',
  name: 'MiVista',
  component: MiVista,
}
```

### Usar datos del backend

1. Agregar método en `src/services/api.ts`
2. Usar en el store correspondiente
3. Llamar desde el componente

```ts
// En api.ts
export const miAPI = {
  obtener: () => API.get('/api/mi-endpoint')
}

// En store
const cargarDatos = async () => {
  const response = await miAPI.obtener()
  datos.value = response.data
}

// En componente
const store = useMiStore()
onMounted(() => store.cargarDatos())
```

---

## 📞 Soporte

Para issues o preguntas:
- Revisar `QUICKSTART.md` en raíz del proyecto
- Verificar que el backend está corriendo
- Revisar logs en consola del navegador (F12)

---

## 🎉 ¡Listo!

El frontend está completamente funcional. Asegúrate de que:

1. ✅ Backend está corriendo en puerto 8000
2. ✅ Instalaste dependencias con `npm install`
3. ✅ Ejecutaste `npm run dev`

¡Abre `http://localhost:5173` y disfruta! 🌾
