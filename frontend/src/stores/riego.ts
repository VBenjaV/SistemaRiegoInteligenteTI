import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { riegoAPI } from '@/services/api'

export const useRiegoStore = defineStore('riego', () => {
  const estado = ref<any>(null)
  const historial = ref<any[]>([])
  const tiempoRiegoHoy = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const riegoActivo = computed(() => estado.value?.activo ?? false)
  const duracionRestante = computed(() => estado.value?.duracion_restante_segundos ?? null)

  const cargarEstado = async (dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await riegoAPI.obtenerEstado(dispositivo_id)
      estado.value = response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando estado:', err)
    } finally {
      loading.value = false
    }
  }

  const cargarHistorial = async (dispositivo_id = 'sensor1', dias = 7) => {
    loading.value = true
    try {
      const response = await riegoAPI.obtenerHistorial(dispositivo_id, 100, 0, dias)
      historial.value = response.data.eventos
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando historial:', err)
    } finally {
      loading.value = false
    }
  }

  const cargarTiempoHoy = async (dispositivo_id = 'sensor1') => {
    try {
      const response = await riegoAPI.obtenerTiempoHoy(dispositivo_id)
      tiempoRiegoHoy.value = response.data.tiempo_total_segundos
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando tiempo:', err)
    }
  }

  const activar = async (duracion_segundos = 300, dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await riegoAPI.forzarOn(dispositivo_id, duracion_segundos)
      if (response.data.exito) {
        await cargarEstado(dispositivo_id)
        await cargarHistorial(dispositivo_id)
      }
      return response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error activando riego:', err)
    } finally {
      loading.value = false
    }
  }

  const desactivar = async (dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await riegoAPI.forzarOff(dispositivo_id)
      if (response.data.exito) {
        await cargarEstado(dispositivo_id)
        await cargarHistorial(dispositivo_id)
      }
      return response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error desactivando riego:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    estado,
    historial,
    tiempoRiegoHoy,
    loading,
    error,
    riegoActivo,
    duracionRestante,
    cargarEstado,
    cargarHistorial,
    cargarTiempoHoy,
    activar,
    desactivar,
  }
})
