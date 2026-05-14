import { defineStore } from 'pinia'
import { ref } from 'vue'
import { climaAPI } from '@/services/api'

export const useClimaStore = defineStore('clima', () => {
  const climaActual = ref<any>(null)
  const pronostico = ref<any[]>([])
  const lluvia24h = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const cargarClima = async (ciudad = 'Mexico City') => {
    loading.value = true
    try {
      const [actual, lluvia] = await Promise.all([
        climaAPI.obtenerPronostico(ciudad),
        climaAPI.obtenerLluvia24h(ciudad),
      ])
      
      climaActual.value = actual.data.clima_actual
      lluvia24h.value = lluvia.data.lluvia_24h_mm
      pronostico.value = actual.data.lluvia_pronostico
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando clima:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    climaActual,
    pronostico,
    lluvia24h,
    loading,
    error,
    cargarClima,
  }
})
