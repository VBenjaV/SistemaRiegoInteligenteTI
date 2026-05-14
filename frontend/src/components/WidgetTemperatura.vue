<template>
  <div class="bg-gradient-to-r from-orange-400 to-orange-600 text-white p-6 rounded-lg shadow-lg">
    <h3 class="text-sm font-semibold opacity-90">Temperatura</h3>
    <div class="text-4xl font-bold my-3">{{ temperatura?.toFixed(1) ?? '-' }}°C</div>
    <p class="text-xs opacity-80">Temperatura actual del ambiente</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  temperatura: number | null
}

withDefaults(defineProps<Props>(), {
  temperatura: null,
})
</script>
