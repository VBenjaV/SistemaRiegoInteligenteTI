import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardAPI } from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const dashboard = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const humedad = computed(() => dashboard.value?.humedad_actual ?? null)
  const temperatura = computed(() => dashboard.value?.temperatura_actual ?? null)
  const riegoActivo = computed(() => dashboard.value?.riego_activo ?? false)
  const duracionRestante = computed(() => dashboard.value?.duracion_riego_restante ?? null)
  const climaTemperatura = computed(() => dashboard.value?.clima_temperatura ?? null)
  const climaLluvia24h = computed(() => dashboard.value?.clima_lluvia_24h ?? null)
  const umbral = computed(() => dashboard.value?.umbral_humedad ?? 40)

  const cargarDashboard = async (dispositivo_id = 'sensor1') => {
    loading.value = true
    error.value = null
    try {
      const response = await dashboardAPI.obtenerActual(dispositivo_id)
      dashboard.value = response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando dashboard:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    dashboard,
    loading,
    error,
    humedad,
    temperatura,
    riegoActivo,
    duracionRestante,
    climaTemperatura,
    climaLluvia24h,
    umbral,
    cargarDashboard,
  }
})
