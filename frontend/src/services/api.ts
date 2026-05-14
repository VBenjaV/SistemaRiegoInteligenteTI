import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

// API de Sensores
export const sensoresAPI = {
  crearLectura: (humedad: number, dispositivo_id = 'sensor1', temperatura?: number) =>
    API.post('/api/sensores/', { humedad, dispositivo_id, temperatura }),
  
  obtenerActual: (dispositivo_id = 'sensor1') =>
    API.get('/api/sensores/actual', { params: { dispositivo_id } }),
  
  obtenerHistorial: (dispositivo_id = 'sensor1', limit = 100, offset = 0, dias?: number) =>
    API.get('/api/sensores/historial', { 
      params: { dispositivo_id, limit, offset, dias } 
    }),
  
  obtenerPromedio: (dispositivo_id = 'sensor1', minutos = 60) =>
    API.get('/api/sensores/promedio', { 
      params: { dispositivo_id, minutos } 
    }),
}

// API de Riego
export const riegoAPI = {
  obtenerEstado: (dispositivo_id = 'sensor1') =>
    API.get('/api/riego/estado', { params: { dispositivo_id } }),
  
  evaluar: (dispositivo_id = 'sensor1') =>
    API.post('/api/riego/evaluar', null, { params: { dispositivo_id } }),
  
  forzarOn: (dispositivo_id = 'sensor1', duracion_segundos = 300) =>
    API.post('/api/riego/forzar-on', {
      accion: 'ON',
      duracion_segundos,
      dispositivo_id
    }),
  
  forzarOff: (dispositivo_id = 'sensor1') =>
    API.post('/api/riego/forzar-off', null, { params: { dispositivo_id } }),
  
  obtenerHistorial: (dispositivo_id = 'sensor1', limit = 50, offset = 0, dias?: number) =>
    API.get('/api/riego/historial', {
      params: { dispositivo_id, limit, offset, dias }
    }),
  
  obtenerTiempoHoy: (dispositivo_id = 'sensor1') =>
    API.get('/api/riego/tiempo-total-hoy', { params: { dispositivo_id } }),
}

// API de Configuración
export const configAPI = {
  obtener: (dispositivo_id = 'sensor1') =>
    API.get('/api/config/', { params: { dispositivo_id } }),
  
  actualizarUmbral: (umbral_humedad: number, dispositivo_id = 'sensor1') =>
    API.put('/api/config/umbral', { umbral_humedad, dispositivo_id }),
  
  actualizarIntervalo: (intervalo_lectura_min: number, dispositivo_id = 'sensor1') =>
    API.put('/api/config/intervalo', { intervalo_lectura_min, dispositivo_id }),
  
  obtenerUmbral: (dispositivo_id = 'sensor1') =>
    API.get('/api/config/umbral', { params: { dispositivo_id } }),
}

// API de Clima
export const climaAPI = {
  obtenerPronostico: (ciudad = 'Mexico City') =>
    API.get('/api/clima/pronostico', { params: { ciudad } }),
  
  obtenerActual: (ciudad = 'Mexico City') =>
    API.get('/api/clima/actual', { params: { ciudad } }),
  
  obtenerLluvia24h: (ciudad = 'Mexico City') =>
    API.get('/api/clima/lluvia-24h', { params: { ciudad } }),
  
  actualizarPronostico: (ciudad = 'Mexico City') =>
    API.post('/api/clima/actualizar-pronostico', null, { params: { ciudad } }),
}

// API de Dashboard
export const dashboardAPI = {
  obtenerActual: (dispositivo_id = 'sensor1') =>
    API.get('/api/dashboard/actual', { params: { dispositivo_id } }),
  
  obtenerResumen: (dispositivo_id = 'sensor1') =>
    API.get('/api/dashboard/resumen', { params: { dispositivo_id } }),
}

export default API
