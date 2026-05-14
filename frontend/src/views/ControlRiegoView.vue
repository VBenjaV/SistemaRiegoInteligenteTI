<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8">💧 Control de Riego</h1>

      <!-- Indicador de estado grande -->
      <div class="bg-white rounded-lg shadow-lg p-8 mb-8 text-center">
        <div :class="['w-32 h-32 rounded-full mx-auto flex items-center justify-center text-white text-center mb-4', 
          riegoStore.riegoActivo ? 'bg-gradient-to-r from-green-500 to-green-700 animate-pulse' : 'bg-gradient-to-r from-gray-500 to-gray-700']">
          <div>
            <p class="text-2xl font-bold">{{ riegoStore.riegoActivo ? '🟢' : '🔴' }}</p>
            <p class="font-bold mt-2">{{ riegoStore.riegoActivo ? 'ENCENDIDO' : 'APAGADO' }}</p>
            <p v-if="riegoStore.duracionRestante" class="text-sm">{{ riegoStore.duracionRestante }}s</p>
          </div>
        </div>
      </div>

      <!-- Controles -->
      <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6">Controles</h2>
        
        <div class="grid md:grid-cols-3 gap-8">
          <!-- Duración -->
          <div>
            <label class="block font-semibold mb-3">Duración (segundos)</label>
            <input 
              v-model.number="duracionSeleccionada" 
              type="number" 
              min="60" 
              max="3600"
              :disabled="riegoStore.riegoActivo"
              class="w-full px-4 py-2 border rounded-lg mb-4"
            />
            <div class="grid grid-cols-3 gap-2">
              <button @click="duracionSeleccionada = 300" class="btn btn-primary text-sm">5 min</button>
              <button @click="duracionSeleccionada = 600" class="btn btn-primary text-sm">10 min</button>
              <button @click="duracionSeleccionada = 1200" class="btn btn-primary text-sm">20 min</button>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex flex-col justify-end gap-4">
            <button 
              @click="activar"
              :disabled="riegoStore.riegoActivo || riegoStore.loading"
              class="btn btn-success py-4 text-lg font-bold disabled:opacity-50"
            >
              🟢 ENCENDER
            </button>
            <button 
              @click="desactivar"
              :disabled="!riegoStore.riegoActivo || riegoStore.loading"
              class="btn btn-danger py-4 text-lg font-bold disabled:opacity-50"
            >
              🔴 APAGAR
            </button>
          </div>

          <!-- Estadísticas del día -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="font-semibold mb-3">Hoy</h3>
            <p class="mb-2">
              <span class="text-gray-600">Tiempo total:</span>
              <span class="font-bold">{{ (riegoStore.tiempoRiegoHoy / 60).toFixed(1) }} min</span>
            </p>
            <p>
              <span class="text-gray-600">Ciclos:</span>
              <span class="font-bold">{{ ciclosHoy }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Historial de eventos -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6">Historial de Eventos</h2>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-100">
              <tr>
                <th class="px-6 py-3 text-left font-semibold">Fecha/Hora</th>
                <th class="px-6 py-3 text-left font-semibold">Acción</th>
                <th class="px-6 py-3 text-left font-semibold">Duración</th>
                <th class="px-6 py-3 text-left font-semibold">Tipo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="evento in riegoStore.historial" :key="evento.id" class="border-b hover:bg-gray-50">
                <td class="px-6 py-3">{{ formatoFecha(evento.timestamp) }}</td>
                <td class="px-6 py-3">
                  <span :class="evento.accion === 'ON' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'">
                    {{ evento.accion }}
                  </span>
                </td>
                <td class="px-6 py-3">{{ evento.duracion_segundos }}s</td>
                <td class="px-6 py-3">
                  <span class="text-sm">{{ evento.manual ? '✅ Manual' : '⚙️ Auto' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { useRiegoStore } from '@/stores/riego'

const riegoStore = useRiegoStore()
const duracionSeleccionada = ref(300)

onMounted(async () => {
  await riegoStore.cargarEstado()
  await riegoStore.cargarHistorial()
  await riegoStore.cargarTiempoHoy()
})

const ciclosHoy = computed(() =>
  riegoStore.historial.filter(e => e.accion === 'ON').length
)

const formatoFecha = (fecha: string) => {
  return new Date(fecha).toLocaleString('es-MX')
}

const activar = async () => {
  await riegoStore.activar(duracionSeleccionada.value)
}

const desactivar = async () => {
  await riegoStore.desactivar()
}
</script>
