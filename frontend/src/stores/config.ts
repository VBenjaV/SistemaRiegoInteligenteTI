import { defineStore } from 'pinia'
import { ref } from 'vue'
import { configAPI } from '@/services/api'

export const useConfigStore = defineStore('config', () => {
  const config = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const cargarConfig = async (dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await configAPI.obtener(dispositivo_id)
      config.value = response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error cargando config:', err)
    } finally {
      loading.value = false
    }
  }

  const actualizarUmbral = async (umbral_humedad: number, dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await configAPI.actualizarUmbral(umbral_humedad, dispositivo_id)
      config.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error actualizando umbral:', err)
    } finally {
      loading.value = false
    }
  }

  const actualizarIntervalo = async (intervalo_lectura_min: number, dispositivo_id = 'sensor1') => {
    loading.value = true
    try {
      const response = await configAPI.actualizarIntervalo(intervalo_lectura_min, dispositivo_id)
      config.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message
      console.error('Error actualizando intervalo:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    config,
    loading,
    error,
    cargarConfig,
    actualizarUmbral,
    actualizarIntervalo,
  }
})
