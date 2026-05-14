<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8">⚙️ Configuración</h1>

      <div class="bg-white rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6">Parámetros de Riego</h2>

        <div class="space-y-6 mb-8">
          <!-- Umbral de humedad -->
          <div class="border-b pb-6">
            <label class="block font-semibold mb-2">Umbral de Humedad (%)</label>
            <input 
              v-model.number="config.umbral_humedad" 
              type="number" 
              min="0" 
              max="100"
              class="w-full md:w-64 px-4 py-2 border rounded-lg"
            />
            <p class="text-sm text-gray-600 mt-2">
              Si la humedad cae por debajo de este valor, se activa el riego automático.
            </p>
          </div>

          <!-- Intervalo de lectura -->
          <div class="border-b pb-6">
            <label class="block font-semibold mb-2">Intervalo de Lectura (minutos)</label>
            <input 
              v-model.number="config.intervalo_lectura_min" 
              type="number" 
              min="1" 
              max="60"
              class="w-full md:w-64 px-4 py-2 border rounded-lg"
            />
            <p class="text-sm text-gray-600 mt-2">
              Cada cuántos minutos se lee el sensor.
            </p>
          </div>

          <!-- Umbral de lluvia -->
          <div class="border-b pb-6">
            <label class="block font-semibold mb-2">Umbral de Lluvia (mm)</label>
            <input 
              v-model.number="config.lluvia_minima_mm" 
              type="number" 
              min="0" 
              max="50"
              step="0.5"
              class="w-full md:w-64 px-4 py-2 border rounded-lg"
            />
            <p class="text-sm text-gray-600 mt-2">
              Si la lluvia esperada es mayor, no se activa el riego automático.
            </p>
          </div>

          <!-- Horas de pronóstico -->
          <div class="pb-6">
            <label class="block font-semibold mb-2">Horas de Pronóstico</label>
            <input 
              v-model.number="config.horas_pronostico" 
              type="number" 
              min="1" 
              max="168"
              class="w-full md:w-64 px-4 py-2 border rounded-lg"
            />
            <p class="text-sm text-gray-600 mt-2">
              Cuántas horas en el futuro considerar para el pronóstico.
            </p>
          </div>
        </div>

        <!-- Botón guardar -->
        <div class="flex gap-4">
          <button 
            @click="guardar"
            :disabled="configStore.loading"
            class="btn btn-success px-8 py-3 text-lg font-bold"
          >
            💾 Guardar Cambios
          </button>
          <button 
            @click="recargar"
            :disabled="configStore.loading"
            class="btn btn-primary px-8 py-3"
          >
            ↻ Recargar
          </button>
        </div>

        <!-- Mensaje de éxito -->
        <div v-if="mensajeExito" class="mt-6 p-4 bg-green-100 text-green-700 rounded-lg font-semibold">
          ✅ Configuración guardada exitosamente
        </div>

        <!-- Mensaje de error -->
        <div v-if="configStore.error" class="mt-6 p-4 bg-red-100 text-red-700 rounded-lg font-semibold">
          ❌ {{ configStore.error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
const mensajeExito = ref(false)
const config = reactive({
  umbral_humedad: 40,
  intervalo_lectura_min: 5,
  lluvia_minima_mm: 5.0,
  horas_pronostico: 24,
})

onMounted(async () => {
  await configStore.cargarConfig()
  if (configStore.config) {
    config.umbral_humedad = configStore.config.umbral_humedad
    config.intervalo_lectura_min = configStore.config.intervalo_lectura_min
    config.lluvia_minima_mm = configStore.config.lluvia_minima_mm
    config.horas_pronostico = configStore.config.horas_pronostico
  }
})

const guardar = async () => {
  await configStore.actualizarUmbral(config.umbral_humedad)
  await configStore.actualizarIntervalo(config.intervalo_lectura_min)
  
  mensajeExito.value = true
  setTimeout(() => {
    mensajeExito.value = false
  }, 3000)
}

const recargar = async () => {
  await configStore.cargarConfig()
}
</script>
