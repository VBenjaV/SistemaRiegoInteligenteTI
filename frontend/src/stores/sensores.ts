import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sensoresAPI } from '@/services/api'

export const useSensoresStore = defineStore('sensores', () => {
  const lecturas = ref<any[]>([])
  const lecuraActual = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const promedioHumedad = computed(() => {
    if (lecturas.value.length === 0) return 0
    const suma = lecturas.value.reduce((acc, l) => acc + l.humedad, 0)
    return suma / lecturas.value.length
  })

  const minimoHumedad = computed(() => {
    if (lecturas.value.length === 0) return 0
    return Math.min(...lecturas.value.map(l => l.humedad))
  })

  const maximoHumedad = computed(() => {
    if (lecturas.value.length === 0) return 0
    return Math.max(...lecturas.value.map(l => l.humedad))
  })

  const cargarActual = async (dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await sensoresAPI.obtenerActual(dispositivo_id)
      lecuraActual.value = response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando lectura actual:', err)
    } finally {
      loading.value = false
    }
  }

  const cargarHistorial = async (
    dispositivo_id = 'sensor1',
    limit = 100,
    offset = 0,
    dias?: number
  ) => {
    loading.value = true
    try {
      const response = await sensoresAPI.obtenerHistorial(dispositivo_id, limit, offset, dias)
      lecturas.value = response.data.lecturas
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando historial:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    lecturas,
    lecuraActual,
    loading,
    error,
    promedioHumedad,
    minimoHumedad,
    maximoHumedad,
    cargarActual,
    cargarHistorial,
  }
})
