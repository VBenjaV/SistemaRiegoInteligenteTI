<template>
  <nav class="bg-white shadow-md sticky top-0 z-50">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🌾</span>
          <h1 class="text-xl font-bold text-gray-800">Riego Inteligente</h1>
        </div>
        
        <ul class="flex gap-8">
          <li>
            <RouterLink 
              to="/" 
              class="text-gray-700 hover:text-blue-600 transition"
              :class="{ 'text-blue-600 font-bold': $route.path === '/' }"
            >
              📊 Dashboard
            </RouterLink>
          </li>
          <li>
            <RouterLink 
              to="/sensores" 
              class="text-gray-700 hover:text-blue-600 transition"
              :class="{ 'text-blue-600 font-bold': $route.path === '/sensores' }"
            >
              📡 Sensores
            </RouterLink>
          </li>
          <li>
            <RouterLink 
              to="/riego" 
              class="text-gray-700 hover:text-blue-600 transition"
              :class="{ 'text-blue-600 font-bold': $route.path === '/riego' }"
            >
              💧 Riego
            </RouterLink>
          </li>
          <li>
            <RouterLink 
              to="/clima" 
              class="text-gray-700 hover:text-blue-600 transition"
              :class="{ 'text-blue-600 font-bold': $route.path === '/clima' }"
            >
              🌦️ Clima
            </RouterLink>
          </li>
          <li>
            <RouterLink 
              to="/config" 
              class="text-gray-700 hover:text-blue-600 transition"
              :class="{ 'text-blue-600 font-bold': $route.path === '/config' }"
            >
              ⚙️ Config
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
nav {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
