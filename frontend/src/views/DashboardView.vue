<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    
    <div class="container mx-auto px-4 py-8">
      <!-- Widgets de resumen -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <WidgetHumedad :humedad="dashboardStore.humedad" />
        <WidgetTemperatura :temperatura="dashboardStore.temperatura" />
        <WidgetRiego 
          :activo="dashboardStore.riegoActivo" 
          :duracion="dashboardStore.duracionRestante"
        />
        <WidgetClima :clima="dashboardStore.climaTemperatura" />
      </div>

      <!-- Control principal de riego -->
      <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6">🎮 Control de Riego</h2>
        
        <div class="grid md:grid-cols-3 gap-6">
          <!-- Indicador de estado -->
          <div class="flex justify-center items-center">
            <div :class="['w-24 h-24 rounded-full flex items-center justify-center text-white text-center', 
              dashboardStore.riegoActivo ? 'bg-green-500 animate-pulse' : 'bg-gray-400']">
              <div>
                <p class="font-bold">{{ dashboardStore.riegoActivo ? 'ENCENDIDO' : 'APAGADO' }}</p>
                <p v-if="dashboardStore.duracionRestante" class="text-sm">{{ dashboardStore.duracionRestante }}s</p>
              </div>
            </div>
          </div>

          <!-- Inputs de configuración -->
          <div>
            <label class="block font-semibold mb-2">Duración (segundos)</label>
            <input 
              v-model.number="duracionRiego" 
              type="number" 
              min="60" 
              max="3600"
              :disabled="dashboardStore.riegoActivo"
              class="w-full px-4 py-2 border rounded-lg"
            />
            <div class="grid grid-cols-3 gap-2 mt-2">
              <button @click="duracionRiego = 300" class="btn btn-primary text-sm">5 min</button>
              <button @click="duracionRiego = 600" class="btn btn-primary text-sm">10 min</button>
              <button @click="duracionRiego = 1200" class="btn btn-primary text-sm">20 min</button>
            </div>
          </div>

          <!-- Botones de control -->
          <div class="flex flex-col gap-4 justify-center">
            <button 
              @click="activarRiego"
              :disabled="dashboardStore.riegoActivo || dashboardStore.loading"
              class="btn btn-success py-4 text-lg font-bold"
            >
              🟢 ENCENDER
            </button>
            <button 
              @click="desactivarRiego"
              :disabled="!dashboardStore.riegoActivo || dashboardStore.loading"
              class="btn btn-danger py-4 text-lg font-bold"
            >
              🔴 APAGAR
            </button>
          </div>
        </div>
      </div>

      <!-- Información del clima -->
      <div class="grid md:grid-cols-2 gap-8 mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-bold mb-4">🌦️ Clima Actual</h3>
          <p v-if="dashboardStore.climaTemperatura" class="text-lg">
            <span class="font-semibold">Temperatura:</span> {{ dashboardStore.climaTemperatura?.toFixed(1) }}°C
          </p>
          <p v-if="dashboardStore.climaLluvia24h" class="text-lg mt-2">
            <span class="font-semibold">Lluvia esperada (24h):</span> {{ dashboardStore.climaLluvia24h?.toFixed(1) }} mm
          </p>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-bold mb-4">✅ Estado Actual</h3>
          <p class="text-lg">
            <span class="font-semibold">Humedad:</span> {{ dashboardStore.humedad?.toFixed(1) }}%
          </p>
          <p class="text-lg mt-2">
            <span class="font-semibold">Umbral:</span> {{ dashboardStore.umbral }}%
          </p>
          <p class="text-lg mt-2">
            <span v-if="dashboardStore.humedad && dashboardStore.humedad < dashboardStore.umbral" class="text-red-600 font-bold">
              ⚠️ Por debajo del umbral - Se recomienda riego
            </span>
            <span v-else class="text-green-600 font-bold">
              ✅ Nivel de humedad normal
            </span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import WidgetHumedad from '@/components/WidgetHumedad.vue'
import WidgetTemperatura from '@/components/WidgetTemperatura.vue'
import WidgetRiego from '@/components/WidgetRiego.vue'
import WidgetClima from '@/components/WidgetClima.vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useRiegoStore } from '@/stores/riego'

const dashboardStore = useDashboardStore()
const riegoStore = useRiegoStore()
const duracionRiego = ref(300)

onMounted(async () => {
  await dashboardStore.cargarDashboard()
  // Recargar cada 30 segundos
  setInterval(() => dashboardStore.cargarDashboard(), 30000)
})

const activarRiego = async () => {
  await riegoStore.activar(duracionRiego.value)
  await dashboardStore.cargarDashboard()
}

const desactivarRiego = async () => {
  await riegoStore.desactivar()
  await dashboardStore.cargarDashboard()
}
</script>
