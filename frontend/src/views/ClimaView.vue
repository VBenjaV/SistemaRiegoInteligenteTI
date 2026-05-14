<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8">🌦️ Información Meteorológica</h1>

      <!-- Clima actual -->
      <div class="bg-gradient-to-r from-blue-400 to-blue-600 text-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-3xl font-bold mb-4">Clima Actual</h2>
        <div class="grid md:grid-cols-3 gap-6">
          <div>
            <p class="text-6xl font-bold">{{ climaStore.climaActual?.temperatura?.toFixed(1) ?? '-' }}°C</p>
            <p class="text-lg mt-2">Temperatura</p>
          </div>
          <div>
            <p class="text-4xl">{{ climaStore.climaActual?.humedad_relativa ?? '-' }}%</p>
            <p class="text-lg">Humedad Relativa</p>
          </div>
          <div>
            <p class="text-2xl capitalize">{{ climaStore.climaActual?.descripcion ?? 'N/A' }}</p>
            <p class="text-lg">Estado</p>
          </div>
        </div>
      </div>

      <!-- Pronóstico 24 horas -->
      <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-4">🌧️ Próximas 24 Horas</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
            <p class="text-gray-600 text-sm">Lluvia Esperada</p>
            <p class="text-4xl font-bold">{{ climaStore.lluvia24h?.toFixed(1) ?? '-' }} mm</p>
          </div>
          <div :class="['p-6 rounded-lg border-l-4', climaStore.lluvia24h < 5 ? 'bg-green-50 border-green-500' : 'bg-yellow-50 border-yellow-500']">
            <p class="text-gray-600 text-sm">Recomendación</p>
            <p class="text-xl font-bold">
              {{ climaStore.lluvia24h < 5 ? '✅ Se recomienda riego' : '⚠️ No se recomienda riego' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Pronóstico 5 días -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6">5 Días Pronóstico</h2>
        <p class="text-sm text-gray-600 mb-4">
          Últimas lecturas meteorológicas disponibles
        </p>
        <div v-if="climaStore.pronostico && climaStore.pronostico.length > 0" class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="(item, index) in climaStore.pronostico.slice(0, 6)" 
            :key="index"
            class="bg-gradient-to-br from-purple-100 to-purple-50 p-4 rounded-lg border border-purple-200"
          >
            <p class="text-sm font-semibold text-gray-700">{{ formatoFecha(item.fecha) }}</p>
            <p class="text-2xl font-bold mt-2">{{ item.temperatura_max?.toFixed(0) ?? '-' }}°</p>
            <p class="text-sm text-gray-600">Max: {{ item.temperatura_max?.toFixed(1) ?? '-' }}°C</p>
            <p class="text-sm text-gray-600">Min: {{ item.temperatura_min?.toFixed(1) ?? '-' }}°C</p>
            <p class="text-sm text-blue-600 font-semibold mt-2">🌧️ {{ item.lluvia_esperada_mm?.toFixed(1) ?? '0' }} mm</p>
          </div>
        </div>
        <p v-else class="text-gray-500">Sin datos de pronóstico disponibles</p>
      </div>

      <!-- Loading state -->
      <div v-if="climaStore.loading" class="text-center text-gray-500 mt-8">
        Cargando información meteorológica...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { useClimaStore } from '@/stores/clima'

const climaStore = useClimaStore()

onMounted(async () => {
  await climaStore.cargarClima()
})

const formatoFecha = (fecha: string) => {
  const date = new Date(fecha)
  return date.toLocaleDateString('es-MX', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}
</script>
