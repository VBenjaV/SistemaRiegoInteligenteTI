<template>
  <div :class="['p-6 rounded-lg shadow-lg text-white', riegoActivo ? 'bg-gradient-to-r from-green-500 to-green-700' : 'bg-gradient-to-r from-gray-500 to-gray-700']">
    <h3 class="text-sm font-semibold opacity-90">Estado de Riego</h3>
    <div class="flex items-center my-3">
      <div :class="['w-6 h-6 rounded-full mr-3', riegoActivo ? 'bg-green-300 animate-pulse' : 'bg-gray-300']"></div>
      <span class="text-2xl font-bold">{{ riegoActivo ? 'ACTIVO' : 'INACTIVO' }}</span>
    </div>
    <p v-if="riegoActivo && duracion" class="text-sm">⏱️ {{ duracion }}s restantes</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  activo: boolean
  duracion: number | null
}

withDefaults(defineProps<Props>(), {
  activo: false,
  duracion: null,
})
</script>
