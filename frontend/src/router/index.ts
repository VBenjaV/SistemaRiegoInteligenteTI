import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import SensoresView from '@/views/SensoresView.vue'
import ControlRiegoView from '@/views/ControlRiegoView.vue'
import ConfiguracionView from '@/views/ConfiguracionView.vue'
import ClimaView from '@/views/ClimaView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
  },
  {
    path: '/sensores',
    name: 'Sensores',
    component: SensoresView,
  },
  {
    path: '/riego',
    name: 'Riego',
    component: ControlRiegoView,
  },
  {
    path: '/config',
    name: 'Configuracion',
    component: ConfiguracionView,
  },
  {
    path: '/clima',
    name: 'Clima',
    component: ClimaView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
