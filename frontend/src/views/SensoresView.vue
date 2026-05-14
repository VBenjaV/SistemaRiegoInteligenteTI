<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8">📡 Sensores</h1>

      <!-- Filtros -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
        <div class="grid md:grid-cols-4 gap-4">
          <div>
            <label class="block font-semibold mb-2">Desde</label>
            <input v-model="filtroFecha" type="date" class="w-full px-4 py-2 border rounded-lg" />
          </div>
          <div>
            <label class="block font-semibold mb-2">Hasta</label>
            <input v-model="filtroFechaHasta" type="date" class="w-full px-4 py-2 border rounded-lg" />
          </div>
          <div>
            <label class="block font-semibold mb-2">Días</label>
            <input v-model.number="filtoDias" type="number" min="1" max="365" class="w-full px-4 py-2 border rounded-lg" />
          </div>
          <div class="flex items-end gap-2">
            <button @click="aplicarFiltros" class="btn btn-primary flex-1">🔍 Filtrar</button>
            <button @click="descargarCSV" class="btn btn-primary flex-1">📥 CSV</button>
          </div>
        </div>
      </div>

      <!-- Tabla de lecturas -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-100">
              <tr>
                <th class="px-6 py-3 text-left font-semibold">Fecha/Hora</th>
                <th class="px-6 py-3 text-left font-semibold">Humedad (%)</th>
                <th class="px-6 py-3 text-left font-semibold">Temperatura (°C)</th>
                <th class="px-6 py-3 text-left font-semibold">Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lectura in sensoresStore.lecturas" :key="lectura.id" class="border-b hover:bg-gray-50">
                <td class="px-6 py-3">{{ formatoFecha(lectura.timestamp) }}</td>
                <td class="px-6 py-3">
                  <div class="flex items-center gap-2">
                    <span>{{ lectura.humedad.toFixed(1) }}%</span>
                    <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        class="h-full bg-green-500" 
                        :style="{ width: lectura.humedad + '%' }"
                      ></div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-3">{{ lectura.temperatura?.toFixed(1) || 'N/A' }}°C</td>
                <td class="px-6 py-3">
                  <span :class="obtenerClaseEstado(lectura.humedad)">
                    {{ obtenerEstado(lectura.humedad) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Estadísticas -->
      <div class="grid md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
          <p class="text-gray-600 text-sm">Promedio</p>
          <p class="text-3xl font-bold">{{ sensoresStore.promedioHumedad.toFixed(1) }}%</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-red-500">
          <p class="text-gray-600 text-sm">Mínimo</p>
          <p class="text-3xl font-bold">{{ sensoresStore.minimoHumedad.toFixed(1) }}%</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
          <p class="text-gray-600 text-sm">Máximo</p>
          <p class="text-3xl font-bold">{{ sensoresStore.maximoHumedad.toFixed(1) }}%</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
          <p class="text-gray-600 text-sm">Total Lecturas</p>
          <p class="text-3xl font-bold">{{ sensoresStore.lecturas.length }}</p>
        </div>
      </div>

      <div v-if="sensoresStore.loading" class="text-center text-gray-500">
        Cargando...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { useSensoresStore } from '@/stores/sensores'

const sensoresStore = useSensoresStore()
const filtroFecha = ref('')
const filtroFechaHasta = ref('')
const filtoDias = ref(7)

onMounted(async () => {
  await sensoresStore.cargarHistorial('sensor1', 100, 0, 7)
})

const formatoFecha = (fecha: string) => {
  return new Date(fecha).toLocaleString('es-MX')
}

const obtenerEstado = (humedad: number) => {
  if (humedad < 30) return 'Muy seco'
  if (humedad < 50) return 'Seco'
  if (humedad < 70) return 'Normal'
  return 'Mojado'
}

const obtenerClaseEstado = (humedad: number) => {
  if (humedad < 50) return 'text-red-600 font-bold'
  if (humedad >= 50 && humedad < 70) return 'text-green-600 font-bold'
  return 'text-blue-600 font-bold'
}

const aplicarFiltros = async () => {
  await sensoresStore.cargarHistorial('sensor1', 100, 0, filtoDias.value)
}

const descargarCSV = () => {
  const csv = [
    ['Fecha/Hora', 'Humedad (%)', 'Temperatura (°C)'],
    ...sensoresStore.lecturas.map(l => [
      formatoFecha(l.timestamp),
      l.humedad.toFixed(2),
      l.temperatura?.toFixed(2) || 'N/A'
    ])
  ]
  const csvContent = csv.map(row => row.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'sensores.csv'
  a.click()
}
</script>
