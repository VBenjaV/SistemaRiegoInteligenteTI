const API_BASE = import.meta.env.VITE_API_BASE || ''

async function request(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`)
    err.status = res.status
    throw err
  }
  return res.json()
}

export function fetchDashboard(dispositivoId = 'esp8266') {
  return request(`/api/dashboard/actual?dispositivo_id=${dispositivoId}`)
}

export function fetchResumen(dispositivoId = 'esp8266') {
  return request(`/api/dashboard/resumen?dispositivo_id=${dispositivoId}`)
}

export function fetchHistorial(dispositivoId = 'esp8266', limit = 30) {
  return request(`/api/sensores/historial?dispositivo_id=${dispositivoId}&limit=${limit}`)
}

export function fetchHealth() {
  return request('/health')
}
