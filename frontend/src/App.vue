<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import Login from './Login.vue'
import { fetchDashboard, fetchResumen, fetchHistorial, fetchHealth, logout, isAuthenticated } from './api'

const POLL_MS = 5000
const dispositivoId = 'esp8266'

const autenticado = ref(false)
const dashboard = ref(null)
const resumen = ref(null)
const historial = ref([])
const error = ref(null)
const apiOk = ref(false)
const loading = ref(true)
const lastUpdate = ref(null)

let timer = null

function verificarAutenticacion() {
  autenticado.value = isAuthenticated()
}

async function loadData() {
  try {
    await fetchHealth()
    apiOk.value = true

    const hist = await fetchHistorial(dispositivoId, 40).catch(() => ({ lecturas: [] }))
    historial.value = (hist.lecturas || []).slice().reverse()

    try {
      dashboard.value = await fetchDashboard(dispositivoId)
    } catch {
      const actual = await fetch(
        `${import.meta.env.VITE_API_BASE || ''}/api/sensores/actual?dispositivo_id=${dispositivoId}`
      )
      if (actual.ok) {
        const s = await actual.json()
        dashboard.value = {
          humedad_actual: s.humedad,
          temperatura_actual: s.temperatura,
          riego_activo: false,
          umbral_humedad: 40,
          clima_ciudad: '—',
          actualizado: s.timestamp,
        }
      }
    }

    try {
      resumen.value = await fetchResumen(dispositivoId)
    } catch {
      resumen.value = null
    }
    error.value = null
    lastUpdate.value = new Date()
  } catch (e) {
    apiOk.value = e.status !== 404
    if (e.status === 404) {
      error.value = 'API conectada. Esperando datos del ESP en IoT Core (ESP8266/pub)...'
      dashboard.value = null
    } else {
      error.value = 'No se pudo conectar al backend. ¿Está corriendo en :8000?'
      apiOk.value = false
    }
  } finally {
    loading.value = false
  }
}

const humedad = computed(() => dashboard.value?.humedad_actual ?? resumen.value?.humedad?.actual)
const temperatura = computed(() => dashboard.value?.temperatura_actual)
const umbral = computed(() => dashboard.value?.umbral_humedad ?? resumen.value?.humedad?.umbral ?? 40)
const riegoActivo = computed(() => dashboard.value?.riego_activo ?? resumen.value?.riego?.activo ?? false)

const humedadEstado = computed(() => {
  const h = humedad.value
  if (h == null) return 'sin-datos'
  if (h < umbral.value) return 'bajo'
  if (h < umbral.value + 15) return 'medio'
  return 'ok'
})

const chartPoints = computed(() => {
  return historial.value.map((l) => ({
    v: l.humedad,
    t: new Date(l.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' }),
  }))
})

const chartPath = computed(() => {
  const pts = chartPoints.value
  if (pts.length < 2) return ''
  const w = 100
  const h = 40
  const max = Math.max(...pts.map((p) => p.v), 100)
  const min = Math.min(...pts.map((p) => p.v), 0)
  const range = max - min || 1
  return pts
    .map((p, i) => {
      const x = (i / (pts.length - 1)) * w
      const y = h - ((p.v - min) / range) * h
      return `${i === 0 ? 'M' : 'L'}${x},${y}`
    })
    .join(' ')
})

function handleLoginSuccess() {
  verificarAutenticacion()
  loadData()
  timer = setInterval(loadData, POLL_MS)
}

function handleLogout() {
  logout()
  verificarAutenticacion()
  if (timer) clearInterval(timer)
}

onMounted(() => {
  verificarAutenticacion()
  if (autenticado.value) {
    loadData()
    timer = setInterval(loadData, POLL_MS)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <!-- Mostrar Login si no está autenticado -->
  <div v-if="!autenticado">
    <Login @login-success="handleLoginSuccess" />
  </div>

  <!-- Mostrar Dashboard si está autenticado -->
  <div v-else class="app">
    <header class="header">
      <div>
        <h1>Sistema de Riego Inteligente</h1>
        <p class="subtitle">Datos en vivo desde AWS IoT Core → MongoDB</p>
      </div>
      <div class="header-right">
        <div class="status-pills">
          <span class="pill" :class="apiOk ? 'ok' : 'err'">
            {{ apiOk ? 'API conectada' : 'API desconectada' }}
          </span>
          <span class="pill device">ESP8266 · {{ dispositivoId }}</span>
        </div>
        <button @click="handleLogout" class="btn-logout">Logout</button>
      </div>
    </header>

    <p v-if="error" class="banner" :class="{ warn: apiOk }">{{ error }}</p>

    <section class="metrics">
      <article class="card metric" :class="humedadEstado">
        <span class="label">Humedad del suelo</span>
        <span class="value">
          {{ humedad != null ? humedad.toFixed(1) : '—' }}
          <small>%</small>
        </span>
        <span class="hint">Umbral de riego: {{ umbral }}%</span>
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{ width: humedad != null ? `${Math.min(humedad, 100)}%` : '0%' }"
          />
          <div class="bar-threshold" :style="{ left: `${umbral}%` }" />
        </div>
      </article>

      <article class="card metric temp">
        <span class="label">Temperatura</span>
        <span class="value">
          {{ temperatura != null ? temperatura.toFixed(1) : '—' }}
          <small>°C</small>
        </span>
        <span class="hint">Sensor ESP8266</span>
      </article>

      <article class="card metric riego" :class="{ active: riegoActivo }">
        <span class="label">Estado de riego</span>
        <span class="value riego-text">{{ riegoActivo ? 'ACTIVO' : 'INACTIVO' }}</span>
        <span v-if="dashboard?.duracion_riego_restante" class="hint">
          Restan {{ dashboard.duracion_riego_restante }} s
        </span>
        <span v-else-if="resumen?.riego?.tiempo_total_hoy_min != null" class="hint">
          Hoy: {{ resumen.riego.tiempo_total_hoy_min }} min
        </span>
      </article>

      <article class="card metric promo" v-if="resumen?.humedad?.promedio_1h != null">
        <span class="label">Promedio 1 h</span>
        <span class="value">{{ resumen.humedad.promedio_1h }}<small>%</small></span>
      </article>
    </section>

    <section class="card chart-card">
      <h2>Historial de humedad</h2>
      <p v-if="chartPoints.length < 2" class="chart-empty">
        Se mostrará el gráfico cuando haya al menos 2 lecturas guardadas.
      </p>
      <div v-else class="chart-wrap">
        <svg viewBox="0 0 100 44" preserveAspectRatio="none" class="chart-svg">
          <path :d="chartPath" fill="none" stroke="var(--green)" stroke-width="1.5" />
        </svg>
        <div class="chart-labels">
          <span>{{ chartPoints[0]?.t }}</span>
          <span>{{ chartPoints[chartPoints.length - 1]?.t }}</span>
        </div>
      </div>
    </section>

    <footer class="footer">
      <span v-if="lastUpdate">
        Actualizado: {{ lastUpdate.toLocaleTimeString('es') }} · cada {{ POLL_MS / 1000 }} s
      </span>
      <a href="http://localhost:8000/docs" target="_blank" rel="noopener">API Docs</a>
    </footer>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.subtitle {
  color: var(--muted);
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.status-pills {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: var(--surface2);
  border: 1px solid var(--border);
}

.pill.ok {
  background: rgba(61, 214, 140, 0.15);
  border-color: var(--green-dim);
  color: var(--green);
}

.pill.err {
  background: rgba(240, 113, 120, 0.15);
  border-color: var(--red);
  color: var(--red);
}

.pill.device {
  color: var(--blue);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
}

.user-email {
  color: var(--muted);
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: none;
  color: #10b981;
  border: 1px solid #10b981;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-logout:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.1);
  border-color: #34d399;
  color: #34d399;
}

.btn-logout:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.banner {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  background: rgba(240, 113, 120, 0.12);
  border: 1px solid var(--red);
  color: var(--red);
  font-size: 0.9rem;
}

.banner.warn {
  background: rgba(245, 185, 66, 0.12);
  border-color: var(--amber);
  color: var(--amber);
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
}

.metric .label {
  display: block;
  font-size: 0.8rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.5rem;
}

.metric .value {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1;
}

.metric .value small {
  font-size: 1rem;
  font-weight: 500;
  color: var(--muted);
}

.metric .hint {
  display: block;
  font-size: 0.8rem;
  color: var(--muted);
  margin-top: 0.5rem;
}

.metric.bajo .value {
  color: var(--red);
}

.metric.medio .value {
  color: var(--amber);
}

.metric.ok .value,
.metric:not(.bajo):not(.medio):not(.sin-datos) .value {
  color: var(--green);
}

.metric.temp .value {
  color: var(--blue);
}

.metric.riego.active {
  border-color: var(--water);
  box-shadow: 0 0 24px rgba(79, 195, 247, 0.2);
}

.riego-text {
  font-size: 1.5rem !important;
  color: var(--water);
}

.metric.riego:not(.active) .riego-text {
  color: var(--muted);
}

.bar-track {
  position: relative;
  height: 6px;
  background: var(--surface2);
  border-radius: 3px;
  margin-top: 1rem;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--green-dim), var(--green));
  border-radius: 3px;
  transition: width 0.4s ease;
}

.bar-threshold {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 10px;
  background: var(--amber);
  transform: translateX(-50%);
}

.chart-card h2 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--muted);
}

.chart-empty {
  color: var(--muted);
  font-size: 0.9rem;
}

.chart-wrap {
  height: 120px;
}

.chart-svg {
  width: 100%;
  height: 100px;
  display: block;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 0.25rem;
}

.footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--muted);
}

.footer a {
  color: var(--green);
  text-decoration: none;
}

.footer a:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-right {
    align-items: stretch;
  }

  .user-info {
    justify-content: space-between;
  }

  .btn-logout {
    width: 100%;
  }
}
</style>
