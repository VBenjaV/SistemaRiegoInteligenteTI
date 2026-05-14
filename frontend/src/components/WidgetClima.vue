<template>
  <div class="bg-gradient-to-r from-blue-400 to-blue-600 text-white p-6 rounded-lg shadow-lg">
    <h3 class="text-sm font-semibold opacity-90">Clima</h3>
    <div class="text-4xl font-bold my-3">{{ clima?.toFixed(1) ?? '-' }}°C</div>
    <p class="text-xs opacity-80">{{ descripcion }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  clima: number | null
  descripcion?: string
}

const props = withDefaults(defineProps<Props>(), {
  clima: null,
  descripcion: 'Clima actual'
})

const descripcion = computed(() => props.descripcion ?? 'Clima actual')
</script>
