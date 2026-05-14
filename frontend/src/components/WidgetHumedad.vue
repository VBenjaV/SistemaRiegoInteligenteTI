<template>
  <div class="bg-gradient-to-r from-purple-500 to-purple-700 text-white p-6 rounded-lg shadow-lg">
    <h3 class="text-sm font-semibold opacity-90">Humedad del Suelo</h3>
    <div class="text-4xl font-bold my-3">{{ humedad?.toFixed(1) ?? '-' }}%</div>
    <div class="w-full bg-gray-300 h-2 rounded-full overflow-hidden">
      <div 
        class="bg-green-400 h-full transition-all duration-300" 
        :style="{ width: (humedad ?? 0) + '%' }"
      ></div>
    </div>
    <p class="text-xs mt-2 opacity-80">{{ estado }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  humedad: number | null
}

const props = withDefaults(defineProps<Props>(), {
  humedad: null,
})

const estado = computed(() => {
  const h = props.humedad
  if (!h) return 'Sin datos'
  if (h < 30) return '🔴 Muy seco'
  if (h < 50) return '🟡 Seco'
  if (h < 70) return '🟢 Óptimo'
  return '🔵 Mojado'
})
</script>
